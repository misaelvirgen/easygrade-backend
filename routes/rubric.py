from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import generate_rubric_with_ai

router = APIRouter()

class RubricRequest(BaseModel):
    assignment_prompt: str
    grade_level: str

@router.post("/generate")
def generate_rubric(data: RubricRequest):
    rubric = generate_rubric_with_ai(
        prompt_text=data.assignment_prompt,
        grade_level=data.grade_level
    )

    return { "rubric": rubric }
