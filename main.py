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

        # Detect edges in the image using Canny edge detection
        edged = cv2.Canny(gray, 170, 200)

        # Find contours in the edged image
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        # Initialize variables for license plate
        license_plate = None

        # Loop through contours to find a rectangle representing the license plate
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)          
            if len(approx) == 4:
                license_plate = approx
                break

        # If a license plate is found
        if license_plate is not None:
            x, y, w, h = cv2.boundingRect(license_plate)
            license_plate_image = gray[y:y + h, x:x + w]
            
            # Use Tesseract to extract text from the license plate image
            license_plate_text = pytesseract.image_to_string(license_plate_image, config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            
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
    license_plate_text = process_image('sample/plat_sample3.png')
    print('License Plate Text:', '\033[1;32m'+license_plate_text+'\033[0m')