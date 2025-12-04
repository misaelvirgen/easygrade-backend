from fastapi import APIRouter, UploadFile, File
from services.extract_service import extract_rubric_text

router = APIRouter()

@router.post("/rubric")
async def upload_rubric(file: UploadFile = File(...)):
    text = await extract_rubric_text(file)
    return {"text": text}
