# Simple placeholder AI grading logic.
# Later, we can swap this for a real OpenAI-based implementation.

def generate_ai_grade(text: str, rubric_json: str):
    words = len(text.split())

    if words > 300:
        score = 90
        feedback = "Well developed essay with ample evidence."
    elif words > 150:
        score = 75
        feedback = "Good essay but could use more depth."
    elif words > 50:
        score = 60
        feedback = "Basic ideas present but needs more development."
    else:
        score = 40
        feedback = "Too short. Needs significant expansion and detail."

    return {"score": score, "feedback": feedback}
