import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def grade_essay_with_ai(prompt_text: str, essay_text: str, rubric_text: str):
    # If rubric is empty, give AI a default fallback rubric
    rubric_block = rubric_text if rubric_text.strip() else """
Score the essay using standard ELA writing criteria:
- Clarity and Organization
- Evidence and Reasoning
- Style and Voice
- Grammar and Conventions
Each category should influence the final holistic score.
"""

    prompt = f"""
You are an expert English teacher. Evaluate the student’s essay based on the assignment prompt and rubric.

### ASSIGNMENT PROMPT
{prompt_text}

### STUDENT ESSAY
{essay_text}

### RUBRIC (optional)
{rubric_block}

### TASK
1. Determine how well the essay addresses the assignment prompt.
2. Score the essay holistically from 0–100.
3. Provide rubric-aligned feedback.
4. Provide 2 strengths.
5. Provide 2 weaknesses.

Return ONLY valid JSON in this exact format:

{{
  "score": <number>,
  "feedback": "<string>",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."]
}}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return completion.choices[0].message.parsed
