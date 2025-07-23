import os
import re
import zipfile
import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
from PyPDF2 import PdfWriter

def extract_value(text, key):
    lines = text.splitlines()
    for line in lines:
        if key in line:
            parts = line.split(key)
            if len(parts) > 1:
                value = parts[1].strip(": -\n\t")
                return value.strip()
    return None

def ocr_pdf_and_split(uploaded_file, key):
    os.makedirs("output_pages", exist_ok=True)
    zip_path = "output.zip"
    zipf = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)

    images = convert_from_bytes(uploaded_file.read(), fmt="jpeg")

    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image)
        value = extract_value(text, key)
        if not value:
            value = f"Unknown_Page_{i+1}"
        filename = f"{value}.pdf"
        filepath = os.path.join("output_pages", filename)

        # Save this image as a single-page PDF
        image.convert("RGB").save(filepath, "PDF")
        zipf.write(filepath, arcname=filename)

    zipf.close()
    return zip_path

# 🖥️ Streamlit UI
st.set_page_config(page_title="OCR PDF Splitter", layout="centered")
st.title("📄 PDF Split & Rename by Key (with OCR)")

uploaded_file = st.file_uploader("Upload a scanned PDF", type=["pdf"])
key = st.text_input("Enter the key to extract value (e.g., Credit Note No)")

if uploaded_file and key:
    if st.button("🔍 Process PDF"):
        with st.spinner("Processing... Please wait."):
            result_zip = ocr_pdf_and_split(uploaded_file, key)
            with open(result_zip, "rb") as f:
                st.success("✅ Done! Download your ZIP file below.")
                st.download_button("📥 Download ZIP", f, file_name="output.zip")
