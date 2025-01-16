import cv2
import numpy as np
from PIL import Image
import pytesseract
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os
import logging
import re  # for regular expressions
from flask_cors import CORS  # Import the CORS module


app = Flask(__name__)
# Enable CORS only for http://localhost:3000
CORS(app, resources={r"/*": {"origins": "*"}})
UPLOAD_FOLDER = 'uploads'

# Create the uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_and_extract_text2(image_path):
    try:
        # Load the image
        image = cv2.imread(image_path)

        # Check if the image is loaded successfully
        if image is None:
            print(f"Error: Unable to load image from '{image_path}'")
            return None

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply bilateral filtering for noise reduction
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # Apply Gaussian blur to reduce noise
        blurred_image = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply thresholding to get a binary image (black and white)
        _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        _, binary_image2 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Find contours (potential characters)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours from left to right
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

        # Initialize an empty list to store the segmented characters
        character_images = []
        
        ######################
        contours2, _ = cv2.findContours(binary_image2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest contour (assuming the license plate is the largest black region)
        largest_contour = max(contours2, key=cv2.contourArea)

        # Get bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Crop the region of interest
        cropped_image = image[y:y+h, x:x+w]

        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'pre-processing.png'), cropped_image)
        samplle = pytesseract.image_to_string(cropped_image, config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        print(samplle)

        # Iterate over contours and extract each character region
        for contour in contours:
            # Get bounding box for each contour
            x, y, w, h = cv2.boundingRect(contour)

            # Filter out small contours (noise) and keep only reasonable sized contours
            if w > 15 and h > 25:  # You can adjust these values based on your license plate size
                # Crop the character region
                character_roi = binary_image[y:y + h, x:x + w]
                character_images.append(character_roi)

                # Optionally, draw the bounding box on the original image
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Use Tesseract OCR to recognize text from each character region
        for _, character_image in enumerate(character_images):
            
            # Use Tesseract to extract text from the license plate image
            license_plate_text = pytesseract.image_to_string(character_image, config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            
            print(license_plate_text)

            # Clean the extracted text by removing non-alphanumeric characters
            cleaned_string = re.sub(r'[^A-Za-z0-9]', '', license_plate_text)

            return cleaned_string

    except Exception as e:
        # Handle exceptions, print an error message, and return None
        print(f"Error processing image '{image_path}': {str(e)}")
        return None

def process_and_extract_text(file_path):
    try:
        # Open the image file using OpenCV
        image = cv2.imread(file_path)
        logging.info(f"Original image shape: {image.shape}")

        # Upscale the image by a factor of 2 using INTER_CUBIC interpolation
        upscale_factor = 2
        upscaled_image = cv2.resize(image, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_CUBIC)
        logging.info(f"Upscaled image shape: {upscaled_image.shape}")
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'upscaled_image.png'), upscaled_image)

        # Sharpen the image using a sharpening kernel
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Sharpening kernel
        sharpened_image = cv2.filter2D(upscaled_image, -1, kernel)
        logging.info("Applied sharpening.")
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'sharpened_image.png'), sharpened_image)

        # Denoise the sharpened image directly
        denoised_image = cv2.fastNlMeansDenoisingColored(sharpened_image, None, 10, 10, 7, 21)  # Apply directly on the sharpened image
        logging.info("Applied denoising to the sharpened image.")
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'denoised_image.png'), denoised_image)

        # Convert the denoised image to grayscale for further processing as needed
        gray_image = cv2.cvtColor(denoised_image, cv2.COLOR_BGR2GRAY)
        logging.info("Converted to grayscale.")
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'gray_image.png'), gray_image)

        # Use PIL to convert the final denoised image back to a format suitable for Tesseract
        pil_image = Image.fromarray(gray_image)  # or from gray_image if you need grayscale
        pil_image_path = os.path.join(UPLOAD_FOLDER, 'pil_image.png')
        pil_image.save(pil_image_path)
        logging.info(f"Saved PIL image at {pil_image_path}")

        # Configuring Tesseract to read horizontal text
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

        # Use pytesseract to read the text from the processed image
        extracted_text = pytesseract.image_to_string(pil_image, config=custom_config)
        print(f"Extracted Text: {extracted_text}")

        return extracted_text
    except Exception as e:
        logging.error(f"Error processing image with OpenCV and pytesseract: {e}")
        return None      
 
@app.route('/pengcit', methods=['POST'])
def create_transaction():
    logging.info(f"Incoming request: {request.method} {request.url}")

    if 'file' not in request.files:
        error_msg = "No file part"
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400

    file = request.files['file']

    if file.filename == '':
        error_msg = "No selected file"
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400

    if file:  # If file exists
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        logging.info(f"File saved to {file_path}")

        # Process the image file with OCR
        extracted_text = process_and_extract_text2(file_path)

        if extracted_text is None:
            return jsonify({"error": "Image processing failed."}), 500
        

    # # Split the extracted text into an array of characters
    # char_array = list(cleaned_string)

    # # Print the array of characters
    # print(char_array)


    
    # Prepare the transaction payload including parameters mapped from extracted text
    transaction = {
        'extracted_text': extracted_text
    }

    print(f"Response: {jsonify(transaction)}")

    return jsonify(transaction), 200


if __name__ == '__main__':
    app.run(port=8087, debug=True)

