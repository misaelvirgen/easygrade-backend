from fastapi import APIRouter

router = APIRouter()

@router.get("/google/assignments")
def list_assignments(token: str, course_id: str = ""):
    """
    Placeholder: in production, call Google Classroom API with the OAuth token.
    For now, return mock assignments.
    """
    return [
        {"id": "g1", "title": "Google Essay 1"},
        {"id": "g2", "title": "Google Essay 2"},
    ]


@router.post("/google/grades")
def push_grade(token: str, course_id: str, assignment_id: str, student_id: str, grade: float):
    """
    Placeholder: simulate posting a grade to Google Classroom.
    """
    return {
        "status": "success",
        "detail": "Grade pushed to Google Classroom (simulated)",
    }
