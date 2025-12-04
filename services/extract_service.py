import docx2txt
import fitz  # PyMuPDF for PDF
import pytesseract
from PIL import Image
import io

async def extract_rubric_text(upload):
    filename = upload.filename.lower()
    content = await upload.read()

    # PDF extraction
    if filename.endswith(".pdf"):
        pdf = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        return text.strip()

    # DOCX extraction
    if filename.endswith(".docx"):
        with open("temp.docx", "wb") as f:
            f.write(content)
        text = docx2txt.process("temp.docx")
        return text.strip()

    # Image extraction (OCR)
    if filename.endswith((".jpg", ".jpeg", ".png")):
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image)
        return text.strip()

    return ""
