from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from services.ai_service import grade_essay_with_ai
from services.supabase_client import supabase
from services.auth import get_current_user

router = APIRouter()

FREE_PLAN_LIMIT = 10


class GradeRequest(BaseModel):
    student_name: str
    assignment_prompt: str
    assignment_text: str
    rubric_json: str


@router.post("/grade")
def grade_assignment(
    data: GradeRequest,
    user=Depends(get_current_user),
):
    user_id = user.id

    profile_res = (
        supabase
        .table("profiles")
        .select("is_premium, essays_used_this_month")
        .eq("id", user_id)
        .single()
        .execute()
    )

    profile = profile_res.data

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    is_premium = profile["is_premium"]
    essays_graded_this_month = profile["essays_used_this_month"] or 0

    if not is_premium and essays_graded_this_month >= FREE_PLAN_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free plan limit reached",
        )

    result = {
    "score": 85,
    "feedback": "Mock grading result for limit testing.",
    "strengths": "Clear structure",
    "weaknesses": "Needs more evidence",
}


    if not is_premium:
        supabase.table("profiles").update(
            {
                "essays_used_this_month": essays_graded_this_month + 1
            }
        ).eq("id", user_id).execute()

    return {
        "student": data.student_name,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "strengths": result.get("strengths"),
        "weaknesses": result.get("weaknesses"),
    }
