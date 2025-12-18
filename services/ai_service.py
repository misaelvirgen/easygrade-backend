import os
import json
from typing import Any, Dict, List, Optional
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Helpers
# ----------------------------

def _safe_json(parsed: Any) -> Dict[str, Any]:
    """
    The OpenAI SDK may give us message.parsed (dict) OR a JSON string in message.content.
    Normalize to dict.
    """
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, str):
        try:
            return json.loads(parsed)
        except Exception:
            return {}
    return {}

def _default_columns_from_scale(scale: Optional[str]) -> List[Dict[str, Any]]:
    """
    Normalize your "scale" field into a set of column labels + default points.
    Points are descending for common rubric use.
    """
    s = (scale or "").lower()

    # Defaults (table-friendly)
    if "4" in s and "1" in s:
        labels = ["4", "3", "2", "1"]
        points = [4, 3, 2, 1]
    elif "exemplary" in s or "proficient" in s or "developing" in s or "beginning" in s:
        labels = ["Exemplary", "Proficient", "Developing", "Beginning"]
        points = [4, 3, 2, 1]
    elif "exceeds" in s or "meets" in s or "approaching" in s or "below" in s:
        labels = ["Exceeds", "Meets", "Approaching", "Below"]
        points = [4, 3, 2, 1]
    else:
        # Safe default
        labels = ["Exemplary", "Proficient", "Developing", "Beginning"]
        points = [4, 3, 2, 1]

    cols = []
    for idx, label in enumerate(labels):
        cols.append({
            "id": f"c{idx+1}",
            "label": label,
            "points": points[idx],
        })
    return cols

def _normalize_rubric_table(
    data: Dict[str, Any],
    fallback_columns: List[Dict[str, Any]],
    criteria: List[str]
) -> Dict[str, Any]:
    """
    Ensure response has:
      rubric: { columns: [...], rows: [...] }
    with each row having:
      { criterion: str, cells: { colId: str } }
    """
    rubric = data.get("rubric")
    if not isinstance(rubric, dict):
        rubric = {}

    columns = rubric.get("columns")
    if not isinstance(columns, list) or len(columns) < 2:
        columns = fallback_columns

    # Ensure each column has id/label/points
    normalized_cols = []
    for i, c in enumerate(columns):
        if not isinstance(c, dict):
            continue
        col_id = str(c.get("id") or f"c{i+1}")
        label = str(c.get("label") or f"Level {i+1}")
        points = c.get("points")
        try:
            points = int(points)
        except Exception:
            # If missing/invalid, give descending points
            points = max(1, 4 - i)
        normalized_cols.append({"id": col_id, "label": label, "points": points})

    if len(normalized_cols) < 2:
        normalized_cols = fallback_columns

    col_ids = [c["id"] for c in normalized_cols]

    rows = rubric.get("rows")
    if not isinstance(rows, list):
        rows = []

    normalized_rows = []

    # If AI returned rows, normalize them
    for r in rows:
        if not isinstance(r, dict):
            continue
        crit = str(r.get("criterion") or "").strip()
        if not crit:
            continue
        cells = r.get("cells")
        if not isinstance(cells, dict):
            cells = {}
        # Ensure a cell for every column
        normalized_cells = {}
        for cid in col_ids:
            val = cells.get(cid, "")
            normalized_cells[cid] = str(val or "").strip()
        normalized_rows.append({"criterion": crit, "cells": normalized_cells})

    # If missing rows or incomplete, create rows from requested criteria
    if len(normalized_rows) == 0 and criteria:
        for crit in criteria:
            normalized_rows.append({
                "criterion": crit,
                "cells": {cid: "" for cid in col_ids}
            })

    return {"columns": normalized_cols, "rows": normalized_rows}

def rubric_table_to_text(title: str, grade_level: str, subject: str, task_type: str, table: Dict[str, Any]) -> str:
    """
    Create a clean, exportable text version for saving/PDF.
    """
    cols = table.get("columns", [])
    rows = table.get("rows", [])

    header = []
    header.append(f"{title}".strip() or "Rubric")
    meta = " • ".join([x for x in [grade_level, subject, task_type] if x])
    if meta:
        header.append(meta)
    header.append("")  # spacer

    col_line = " | ".join([f"{c.get('label','')}".strip() for c in cols])
    pts_line = " | ".join([f"{int(c.get('points',0))} pts" for c in cols])
    header.append(f"Levels: {col_line}")
    header.append(f"Points: {pts_line}")
    header.append("")

    body = []
    for r in rows:
        crit = r.get("criterion", "").strip()
        if not crit:
            continue
        body.append(f"CRITERION: {crit}")
        cells = r.get("cells", {})
        for c in cols:
            cid = c.get("id")
            label = str(c.get("label", "")).strip()
            desc = str(cells.get(cid, "") or "").strip()
            body.append(f"- {label}: {desc}")
        body.append("")

    return "\n".join(header + body).strip()


# ----------------------------
# Existing grading function (unchanged)
# ----------------------------

def grade_essay_with_ai(prompt_text: str, essay_text: str, rubric_text: str):
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
        response_format={"type": "json_object"},
    )

    parsed = getattr(completion.choices[0].message, "parsed", None)
    if parsed is None:
        parsed = completion.choices[0].message.content
    return _safe_json(parsed)


# ----------------------------
# NEW: Table rubric generation
# ----------------------------

def generate_rubric_table_with_ai(
    title: str,
    grade_level: str,
    subject: str,
    task_type: str,
    criteria: List[str],
    scale: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns:
      {
        "rubric": { "columns": [...], "rows": [...] },
        "rubric_text": "..."
      }
    """
    fallback_columns = _default_columns_from_scale(scale)

    # Instruct AI to fill the table structure, not prose style.
    col_spec = [{"id": c["id"], "label": c["label"]} for c in fallback_columns]

    criteria_list = "\n".join([f"- {c}" for c in criteria]) if criteria else "- (choose 3–6 typical criteria)"

    prompt = f"""
You are an expert curriculum designer.

Create a teacher-ready, table-based rubric for the assignment below.
IMPORTANT: Control the STRUCTURE (table cells), not tone.

### CONTEXT
Title: {title}
Grade Level: {grade_level}
Subject: {subject}
Task Type: {task_type}

### CRITERIA (use these exactly)
{criteria_list}

### PERFORMANCE LEVEL COLUMNS (use these ids + labels exactly)
{json.dumps(col_spec, ensure_ascii=False)}

### OUTPUT RULES
Return ONLY valid JSON.
Return a single object with this exact shape:

{{
  "rubric": {{
    "columns": [
      {{ "id": "c1", "label": "Exemplary", "points": 4 }},
      ...
    ],
    "rows": [
      {{
        "criterion": "Evidence & Support",
        "cells": {{
          "c1": "Brief, specific description for top performance",
          "c2": "Brief, specific description",
          "c3": "Brief, specific description",
          "c4": "Brief, specific description"
        }}
      }}
    ]
  }}
}}

### QUALITY BAR
- Keep each cell concise (1–2 sentences max).
- Make differences between levels clear and observable.
- Align criteria to the task type (presentation includes delivery/visuals; research includes sources/citations; lab includes methods/data).
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    parsed = getattr(completion.choices[0].message, "parsed", None)
    if parsed is None:
        parsed = completion.choices[0].message.content

    data = _safe_json(parsed)

    table = _normalize_rubric_table(data, fallback_columns, criteria)
    rubric_text = rubric_table_to_text(title, grade_level, subject, task_type, table)

    return {
        "rubric": table,
        "rubric_text": rubric_text,
    }
