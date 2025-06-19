# 🚘 Plate Recognition with OpenCV, Tesseract, Flask & Flutter

This is a license plate recognition prototype that combines **computer vision** with a **mobile user interface**. The project uses **Python**, **OpenCV**, **Tesseract OCR**, **Flask**, and a **Flutter UI** to demonstrate how automatic license plate detection could streamline toll systems and traffic management.

---

## 🧰 Tech Stack

| Layer        | Technology               |
|--------------|---------------------------|
| Backend      | Python, Flask             |
| Computer Vision | OpenCV, Tesseract OCR  |
| Frontend     | Flutter                   |
| API Testing  | Postman                   |

---

## 🎯 Features

### ✅ Backend
- Accepts image uploads
- Extracts plate number using OCR
- Returns extracted text to client

### 📱 Frontend (Flutter)
- Simple UI with:
  - Button to pick image
  - Button to send image to Flask backend
  - Display of detected plate number as response

---

## 🖼 Screenshots

| Before Upload | After Upload |
|---------------|--------------|
| UI with image upload button | Plate number extracted and shown |

---


## 🚀 How to Run

### 1. Install dependencies
```bash
pip install flask opencv-python pytesseract

