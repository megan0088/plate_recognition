import cv2
import pytesseract
import numpy as np

# Specify the path to the Tesseract executable (if it's not in your PATH)
# For example, on Windows: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# On Linux or macOS, it might already be in your PATH

def process_image(image_path):
    # Load the license plate image
    image = cv2.imread(image_path)

    resize_image = cv2.resize( 
        image, None, fx = 2, fy = 2,  
        interpolation = cv2.INTER_CUBIC)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Apply thresholding to get a binary image (black and white)
    _, binary_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

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

    # Show the detected characters
    for idx, character_image in enumerate(character_images):
        cv2.imshow(f"Character {idx + 1}", character_image)

    # Show the original image with bounding boxes
    cv2.imshow("License Plate Character Segmentation", image)

    # Use Tesseract OCR to recognize text from each character region
    for idx, character_image in enumerate(character_images):
        # Convert character region to string using pytesseract
        # The output text will be returned as a string
        text = pytesseract.image_to_string(character_image, config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')  # --psm 10 for single character
        print(f"Character {idx + 1} recognized as: {text.strip()}")

    # Show number of characters detected
    print(f"Number of characters detected: {len(character_images)}")

    # text2 = pytesseract.image_to_string(image, lang ='eng', config ='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    # print(f"text 2: {text2}")
    # print(f"length of text 2: {len(text2)}")

    # huruf = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # angka = '0123456789'

    # for i in range (len(text2)):
    #     print(f"jajal yg ke {i+1}: {text2[i]}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    license_plate_text1 = process_image('sample/plat_sample1.jpg')
    print('License Plate Text 1:', '\033[1;32m'+license_plate_text1+'\033[0m')