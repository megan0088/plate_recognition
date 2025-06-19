import cv2
import pytesseract
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os
import logging
import re
from flask_cors import CORS

# === Inisialisasi Config ===
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Fungsi Ekstraksi Teks ===
def process_and_extract_text(image_path):
    try:
        image = cv2.imread(image_path)

        if image is None:
            print(f"Error: Unable to load image from '{image_path}'")
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

        character_images = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 15 and h > 25:
                character_roi = binary_image[y:y + h, x:x + w]
                character_images.append(character_roi)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'image_drawed_bounding_box.png'), image)

        for idx, character_image in enumerate(character_images):
            cv2.imwrite(os.path.join(UPLOAD_FOLDER, f'character_image_{idx}.png'), character_image)
            license_plate_text = pytesseract.image_to_string(
                character_image,
                config='--psm 10 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"'

            )
            print(license_plate_text)
            cleaned_string = re.sub(r'[^A-Za-z0-9 ]', '', license_plate_text)
            return cleaned_string

    except Exception as e:
        print(f"Error processing image '{image_path}': {str(e)}")
        return None

# === Fungsi Konversi Angka ke Huruf (Template Matching) ===
def transform_numeric_to_char(text):
    numeric_to_alpha = {
        '0': 'O', '1': 'I', '2': 'Z', '5': 'S', '6': 'G', '8': 'O'
    }
    return ''.join(numeric_to_alpha.get(char, char) if char.isdigit() else char for char in text)

# === API Endpoint ===
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

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        logging.info(f"File saved to {file_path}")

        extracted_text = process_and_extract_text(file_path)

        if extracted_text is None:
            return jsonify({"error": "Image processing failed."}), 500
        else:
            parts = extracted_text.split()
            part1 = parts[0] if len(parts) > 0 else ""
            part2 = parts[1] if len(parts) > 1 else ""
            part3 = parts[2] if len(parts) > 2 else ""

            part1 = transform_numeric_to_char(part1)
            if part3 != "":
                part3 = transform_numeric_to_char(part3)

            final_text = (part1 + part2 + part3).upper()

            transaction = {
                'extracted_text': final_text
            }
            return jsonify(transaction), 200

# === Menjalankan Aplikasi ===
if __name__ == '__main__':
    app.run(port=8087, debug=True)
