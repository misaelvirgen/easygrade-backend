from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import grade_essay_with_ai

router = APIRouter()

class GradeRequest(BaseModel):
    student_name: str
    assignment_prompt: str
    assignment_text: str
    rubric_json: str

@router.post("/grade")
def grade_assignment(data: GradeRequest):
    result = grade_essay_with_ai(
        prompt_text=data.assignment_prompt,
        essay_text=data.assignment_text,
        rubric_text=data.rubric_json
    )

    return {
        "student": data.student_name,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "strengths": result.get("strengths"),
        "weaknesses": result.get("weaknesses")
    }
