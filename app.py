import os
import re
import zipfile
import pdfplumber
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter

def extract_value(text, key):
    # Try exact match first
    lines = text.splitlines()
    for line in lines:
        if key in line:
            # Example line: "Credit Note No: 1800000002"
            parts = line.split(key)
            if len(parts) > 1:
                value = parts[1].strip(": -\n\t")
                value = value.strip()
                return value
    return None


def split_pdf(file, key):
    temp_dir = "output_pages"
    os.makedirs(temp_dir, exist_ok=True)
    zip_path = "output.zip"

    with open("uploaded.pdf", "wb") as f:
        f.write(file.read())

    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

    with pdfplumber.open("uploaded.pdf") as pdf:
        reader = PdfReader("uploaded.pdf")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            value = extract_value(text, key)
            if not value:
                value = f"Unknown_Page_{i+1}"
            filename = f"{value}.pdf"
            filepath = os.path.join(temp_dir, filename)

            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            with open(filepath, "wb") as f_out:
                writer.write(f_out)

            zipf.write(filepath, arcname=filename)

    zipf.close()
    return zip_path

# 🎯 Streamlit UI
st.title("📄 PDF Split & Rename by Key")
uploaded_file = st.file_uploader("Upload PDF File", type="pdf")
key = st.text_input("Enter Key (e.g., Credit Note No)")

if uploaded_file and key:
    if st.button("Process PDF"):
        zip_result = split_pdf(uploaded_file, key)
        with open(zip_result, "rb") as f:
            st.download_button("📥 Download ZIP", f, file_name="output.zip")
