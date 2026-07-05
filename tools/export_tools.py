from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from agents.schemas import MEDICAL_DISCLAIMER


OUTPUT_DIR = Path("outputs")


def safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", filename.strip())
    cleaned = cleaned.strip("._")
    return cleaned or "medtutor_output.txt"


def generate_output_file(filename: str, content: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / safe_filename(filename)
    path.write_text(content, encoding="utf-8")
    return str(path)


def mcqs_to_markdown(mcqs: list[dict[str, Any]], title: str = "MedTutor MCQs") -> str:
    lines = [f"# {title}", "", f"> {MEDICAL_DISCLAIMER}", ""]
    for index, mcq in enumerate(mcqs, start=1):
        lines.extend([f"## Question {index}", "", mcq["question"], ""])
        for option in mcq["options"]:
            lines.append(f"- {option['label']}. {option['text']}")
        lines.extend(["", f"**Correct answer:** {mcq['correct_answer']}", "", "**Explanations**"])
        for label, explanation in mcq["explanations"].items():
            lines.append(f"- {label}. {explanation}")
        if mcq.get("source_chunks"):
            lines.extend(["", f"**Sources:** {', '.join(mcq['source_chunks'])}"])
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def osce_to_markdown(cases: list[dict[str, Any]], title: str = "MedTutor OSCE Cases") -> str:
    lines = [f"# {title}", "", f"> {MEDICAL_DISCLAIMER}", ""]
    for index, case in enumerate(cases, start=1):
        lines.extend([f"## Station {index}: {case['station_title']}", "", "### Stem", case["stem"], ""])
        lines.append("### Examiner Questions")
        for question in case["examiner_questions"]:
            lines.append(f"- {question}")
        lines.extend(["", "### Expected Answers"])
        for answer in case["expected_answers"]:
            lines.append(f"- {answer}")
        lines.extend(["", "### Common Mistakes"])
        for mistake in case["common_mistakes"]:
            lines.append(f"- {mistake}")
        lines.extend(["", "### Scoring Checklist"])
        for item in case["scoring_checklist"]:
            lines.append(f"- {item}")
        if case.get("source_chunks"):
            lines.extend(["", f"**Sources:** {', '.join(case['source_chunks'])}"])
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def blueprint_to_markdown(blueprint: dict[str, Any]) -> str:
    lines = ["# MedTutor Study Blueprint", "", f"> {MEDICAL_DISCLAIMER}", ""]
    for key, value in blueprint.items():
        heading = key.replace("_", " ").title()
        lines.append(f"## {heading}")
        if isinstance(value, list):
            lines.extend(f"- {item}" for item in value)
        elif isinstance(value, dict):
            lines.extend(f"- {k}: {v}" for k, v in value.items())
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def mcqs_to_csv(mcqs: list[dict[str, Any]]) -> str:
    rows: list[dict[str, str]] = []
    for mcq in mcqs:
        option_map = {option["label"]: option["text"] for option in mcq["options"]}
        rows.append(
            {
                "id": mcq.get("id", ""),
                "question": mcq["question"],
                "a": option_map.get("A", ""),
                "b": option_map.get("B", ""),
                "c": option_map.get("C", ""),
                "d": option_map.get("D", ""),
                "e": option_map.get("E", ""),
                "correct_answer": mcq["correct_answer"],
                "sources": "; ".join(mcq.get("source_chunks", [])),
            }
        )

    fieldnames = ["id", "question", "a", "b", "c", "d", "e", "correct_answer", "sources"]
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def to_pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
