from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.ai_service import generate_ai_grade

router = APIRouter()

class GradeRequest(BaseModel):
    student_name: str = "Unknown"
    assignment_text: str
    rubric_json: str = "{}"

class BatchGradeRequest(BaseModel):
    assignments: List[GradeRequest]


@router.post("/grade")
def grade_single(req: GradeRequest):
    """
    Simple grading endpoint using placeholder AI logic.
    """
    try:
        result = generate_ai_grade(req.assignment_text, req.rubric_json)
        return {
            "student": req.student_name,
            "score": result.get("score"),
            "feedback": result.get("feedback"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grade/batch")
def grade_batch(req: BatchGradeRequest):
    """
    Batch grading endpoint – simple loop over assignments.
    """
    try:
        results = []
        for a in req.assignments:
            r = generate_ai_grade(a.assignment_text, a.rubric_json)
            results.append(
                {
                    "student": a.student_name,
                    "score": r.get("score"),
                    "feedback": r.get("feedback"),
                }
            )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
