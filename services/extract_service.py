import docx2txt
import fitz  # PyMuPDF for PDF

async def extract_rubric_text(upload):
    filename = upload.filename.lower()
    content = await upload.read()

    # ---------------------------
    # PDF extraction
    # ---------------------------
    if filename.endswith(".pdf"):
        try:
            pdf = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in pdf:
                text += page.get_text()
            return text.strip()
        except Exception as e:
            print("PDF extraction error:", e)
            return ""

    # ---------------------------
    # DOCX extraction
    # ---------------------------
    if filename.endswith(".docx"):
        try:
            temp_path = "temp_rubric.docx"
            with open(temp_path, "wb") as f:
                f.write(content)

            text = docx2txt.process(temp_path)
            return text.strip()
        except Exception as e:
            print("DOCX extraction error:", e)
            return ""

    # ---------------------------
    # Image extraction (disabled for now)
    # ---------------------------
    if filename.endswith((".jpg", ".jpeg", ".png")):
        return "Image OCR is not supported yet."

    # ---------------------------
    # Unsupported file types
    # ---------------------------
    return ""
