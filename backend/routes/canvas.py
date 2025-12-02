from fastapi import APIRouter

router = APIRouter()

@router.get("/canvas/assignments")
def get_canvas_assignments(api_token: str, course_id: str = ""):
    """
    Placeholder: in production, call the Canvas API using the API token.
    """
    return [
        {"id": "c1", "name": "Canvas Essay 1"},
        {"id": "c2", "name": "Canvas Essay 2"},
    ]


@router.post("/canvas/grades")
def push_canvas_grade(api_token: str, course_id: str, assignment_id: str, student_id: str, grade: float):
    """
    Placeholder: simulate posting a grade to Canvas.
    """
    return {
        "status": "success",
        "detail": "Grade pushed to Canvas (simulated)",
    }
