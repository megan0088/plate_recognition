# OpenCV for image processing
import cv2                 
# Tesseract for text extraction
import pytesseract         
# Pandas for data manipulation
import pandas as pd        
# Regular expressions for text pattern matching
import re   

# Process an image and extract the license plate text
def process_image(image_path):
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
        _, binary_image = cv2.threshold(blurred_image, 150, 255, cv2.THRESH_BINARY_INV)

        # Find contours (potential characters)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours from left to right
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

        # Initialize an empty list to store the segmented characters
        character_images = []

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
            
            # Clean the extracted text by removing non-alphanumeric characters
            cleaned_string = re.sub(r'[^A-Za-z0-9]', '', license_plate_text)

            return cleaned_string

    except Exception as e:
        # Handle exceptions, print an error message, and return None
        print(f"Error processing image '{image_path}': {str(e)}")
        return None

def template_matching(license_plate_text):
    return ""

if __name__ == "__main__":
    license_plate_text1 = process_image('sample/plat_sample1.jpg')
    print('License Plate Text 1:', '\033[1;32m'+license_plate_text1+'\033[0m')
    license_plate_text2 = process_image('sample/plat_sample2.png')
    print('License Plate Text 2:', '\033[1;32m'+license_plate_text2+'\033[0m')
    license_plate_text3 = process_image('sample/plat_sample3.png')
    print('License Plate Text 3:', '\033[1;32m'+license_plate_text3+'\033[0m')
    license_plate_text4 = process_image('sample/plat_sample4.jpg')
    print('License Plate Text 4:', '\033[1;32m'+license_plate_text4+'\033[0m')
    license_plate_text5 = process_image('sample/plat_sample5.png')
    print('License Plate Text 5:', '\033[1;32m'+license_plate_text5+'\033[0m')