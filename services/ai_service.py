from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def grade_essay_with_ai(essay_text: str, rubric_text: str):
    prompt = f"""
You are an expert English teacher. Grade the following essay according to the rubric.

### RUBRIC
{rubric_text}

### ESSAY
{essay_text}

### TASK
1. Provide a holistic score from 0–100.
2. Provide specific, constructive feedback.
3. Provide 2 strengths.
4. Provide 2 weaknesses.

Return ONLY valid JSON in this format:

{{
  "score": <number>,
  "feedback": "<string>",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."]
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        response_format="json"
    )

    return response.output_json
