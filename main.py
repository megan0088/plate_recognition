import cv2
import pytesseract
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os
import logging
import re 
from flask_cors import CORS

## Start - Inisialisasi Config
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
## End - Inisialisasi Config

# Fungsi peng-ekstrak text
def process_and_extract_text(image_path):
    try:
        # Load gambar
        image = cv2.imread(image_path)

        # Check gambar sukses ter-load apa tidak
        if image is None:
            print(f"Error: Unable to load image from '{image_path}'")
            return None

        # Convert gambar ke grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Implementasi noise reduction pada gambar grayscale
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # Ubah gambar menjadi binary (hitam & putih)
        _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Mencari kontur potensial karakter
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Mengurutkan kontur dari kiri ke kanan
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

        # Inisiasi variable
        character_images = []

        # Iterasi pada kontur yg telah dicari dan meng-ekstrak karakter
        for contour in contours:
            # Mendapatkan koordinat kotak pembatas pada setiap kontur
            x, y, w, h = cv2.boundingRect(contour)

            # Penyaringan kontur
            if w > 15 and h > 25: 
                # Crop karakter
                character_roi = binary_image[y:y + h, x:x + w]
                character_images.append(character_roi)

                # Optionally, draw the bounding box on the original image
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'image_drawed_bounding_box.png'), image)

        # Mengenali text pada variable yang telah di inisiasi sebelumnya menggunakan Tesseract OCR
        for idx, character_image in enumerate(character_images):

            cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'character_image.png'), character_image)
            
            license_plate_text = pytesseract.image_to_string(character_image, config='--psm 10 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "')
            print(license_plate_text)

            # Pembersihan text
            cleaned_string = re.sub(r'[^A-Za-z0-9 ]', '', license_plate_text)

            return cleaned_string

    except Exception as e:
        # Handling error, akan mencetak informasi pada log jika terjadi error
        print(f"Error processing image '{image_path}': {str(e)}")
        return None 

# Fungsi transformasi numerik ke karakter (template matching) 
def transform_numeric_to_char(text):
    numeric_to_alpha = {
        '0': 'O', '1': 'I', '2': 'Z', '5': 'S', '6': 'G', '8': '0'
    }

    return ''.join(numeric_to_alpha[char] if char.isdigit() else char for char in text)


# Fungsi untuk berkomunikasi dengan frontend
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

        #  Process ekstraksi text pada gambar
        extracted_text = process_and_extract_text(file_path)

        if extracted_text is None: # Jika proses ekstraksi gagal
            return jsonify({"error": "Image processing failed."}), 500
        else: # Jika proses ekstraksi berhasil

            # Melakukan split karakter yg terekstrak menjadi 3 bagian
            parts = extracted_text.split()
            part1 = parts[0] if len(parts) > 0 else ""
            part2 = parts[1] if len(parts) > 1 else ""
            part3 = parts[2] if len(parts) > 2 else ""

            # Melakukan template matching untuk menyesuaikan bagian pertama dari plat nomor
            part1 = transform_numeric_to_char(part1)

            # Melakukan template matching untuk menyesuaikan bagian ketiga dari plat nomor
            if part3 != "":
                part3 = transform_numeric_to_char(part3)

            # Finalisasi
            extracted_text = part1+part2+part3
            extracted_text = extracted_text.upper()


    # Setup hasil ekstraksi text untuk di kembalikan pada frontend
    transaction = {
        'extracted_text': extracted_text
    }

    return jsonify(transaction), 200


# Main function
if __name__ == '__main__':
    app.run(port=8087, debug=True)
