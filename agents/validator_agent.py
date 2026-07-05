from __future__ import annotations

from typing import Any

from agents.schemas import LectureChunk, MEDICAL_DISCLAIMER
from tools.lecture_tools import tokenize
from tools.security_tools import run_security_checks


class MedicalSafetyValidatorAgent:
    name = "Medical Safety Validator Agent"

    def validate_input(self, text: str) -> dict[str, Any]:
        return run_security_checks(text)

    def validate_mcqs(self, mcqs: list[dict[str, Any]], chunks: list[LectureChunk]) -> dict[str, Any]:
        lecture_text = " ".join(chunk.text for chunk in chunks)
        lecture_tokens = set(tokenize(lecture_text))
        items: list[dict[str, Any]] = []
        valid = True

        for mcq in mcqs:
            issues: list[str] = []
            options = mcq.get("options", [])
            labels = [option.get("label") for option in options]
            correct_answer = mcq.get("correct_answer")

            if len(options) != 5:
                issues.append("MCQ does not have exactly five options.")
            if labels.count(correct_answer) != 1:
                issues.append("MCQ does not have exactly one best answer.")
            if len({option.get("text", "").strip().lower() for option in options}) != len(options):
                issues.append("Duplicate or near-duplicate answer options detected.")
            if not mcq.get("explanations"):
                issues.append("Missing option explanations.")
            if not mcq.get("source_chunks"):
                issues.append("Missing source references.")

            supported = self._is_supported(mcq, lecture_tokens)
            if not supported:
                issues.append("Correct answer or explanation appears weakly grounded in the lecture.")

            if issues:
                valid = False
            items.append({"id": mcq.get("id", "unknown"), "valid": not issues, "issues": issues})

        return {
            "valid": valid,
            "items": items,
            "disclaimer": MEDICAL_DISCLAIMER,
            "summary": "All MCQs passed validation." if valid else "Some MCQs need review.",
        }

    def repair_mcqs(self, mcqs: list[dict[str, Any]], validation: dict[str, Any]) -> list[dict[str, Any]]:
        issue_map = {item["id"]: item["issues"] for item in validation.get("items", [])}
        repaired: list[dict[str, Any]] = []
        for mcq in mcqs:
            clone = dict(mcq)
            issues = issue_map.get(mcq.get("id"), [])
            if "Missing option explanations." in issues:
                clone["explanations"] = {
                    option["label"]: "Review this option against the lecture source."
                    for option in clone.get("options", [])
                }
            if "Missing source references." in issues:
                clone["source_chunks"] = ["source_not_available"]
            repaired.append(clone)
        return repaired

    def _is_supported(self, mcq: dict[str, Any], lecture_tokens: set[str]) -> bool:
        correct = mcq.get("correct_answer")
        options = {option.get("label"): option.get("text", "") for option in mcq.get("options", [])}
        correct_tokens = set(tokenize(options.get(correct, "")))
        if not correct_tokens:
            return False
        return len(correct_tokens & lecture_tokens) >= min(4, max(1, len(correct_tokens) // 5))

