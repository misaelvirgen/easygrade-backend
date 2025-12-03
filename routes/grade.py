from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import grade_essay_with_ai

router = APIRouter()

class GradeRequest(BaseModel):
    student_name: str
    assignment_text: str
    rubric_json: str

@router.post("/grade")
def grade_assignment(data: GradeRequest):
    result = grade_essay_with_ai(
        essay_text=data.assignment_text,
        rubric_text=data.rubric_json
    )

    return {
        "student": data.student_name,
        "score": result["score"],
        "feedback": result["feedback"],
        "strengths": result["strengths"],
        "weaknesses": result["weaknesses"]
    }
