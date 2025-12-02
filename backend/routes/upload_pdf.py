from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz  # PyMuPDF

router = APIRouter()

@router.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file and returns extracted text.
    """
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text = "".join([page.get_text() for page in doc])
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
