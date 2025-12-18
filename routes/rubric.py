from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.ai_service import generate_rubric_table_with_ai

router = APIRouter()

class RubricRequest(BaseModel):
    # Accept both camelCase (frontend) and snake_case (backend-friendly)
    title: str = Field(..., alias="title")
    grade_level: str = Field(..., alias="gradeLevel")
    subject: str = Field(..., alias="subject")
    task_type: str = Field(..., alias="taskType")
    criteria: List[str] = Field(default_factory=list, alias="criteria")
    scale: Optional[str] = Field(default=None, alias="scale")

    class Config:
        populate_by_name = True  # allow using pythonic field names internally


@router.post("/generate")
def generate_rubric(data: RubricRequest):
    result = generate_rubric_table_with_ai(
        title=data.title,
        grade_level=data.grade_level,
        subject=data.subject,
        task_type=data.task_type,
        criteria=data.criteria,
        scale=data.scale,
    )
    # Return both: structured rubric + exportable text
    return result
