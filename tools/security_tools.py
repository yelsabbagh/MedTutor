from __future__ import annotations

import re
from typing import Any


SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "send api key",
    "disable safety",
    "act as developer",
    "jailbreak",
    "forget your instructions",
    "show hidden prompt",
]


PHI_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b"),
    "medical_record_number": re.compile(r"\b(?:MRN|medical record|hospital number)\s*[:#-]?\s*[A-Z0-9-]{5,}\b", re.IGNORECASE),
    "national_id": re.compile(r"\b(?:national id|ssn|social security)\s*[:#-]?\s*\d{3,}[-\d]*\b", re.IGNORECASE),
    "patient_name": re.compile(r"\b(?:patient name|name)\s*[:#-]\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"),
    "address": re.compile(r"\b\d{1,5}\s+[A-Za-z0-9 .'-]+\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln)\b", re.IGNORECASE),
}


def scan_prompt_injection(text: str) -> dict[str, Any]:
    lowered = text.lower()
    matches = [pattern for pattern in SUSPICIOUS_PATTERNS if pattern in lowered]
    return {
        "risk": "prompt_injection" if matches else "none",
        "safe": not matches,
        "matches": matches,
        "action": "ignored suspicious instruction inside document" if matches else "none",
    }


def validate_no_phi(text: str) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for label, pattern in PHI_PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append({"type": label, "sample": _redact(match.group(0))})

    return {
        "safe": not findings,
        "risk": "possible_phi" if findings else "none",
        "findings": findings,
        "message": (
            "Possible PHI detected. Use de-identified lecture material only."
            if findings
            else "No obvious PHI patterns detected."
        ),
    }


def run_security_checks(text: str) -> dict[str, Any]:
    prompt_injection = scan_prompt_injection(text)
    phi = validate_no_phi(text)
    return {
        "safe": prompt_injection["safe"] and phi["safe"],
        "prompt_injection": prompt_injection,
        "phi": phi,
    }


def _redact(value: str) -> str:
    compact = value.strip()
    if len(compact) <= 6:
        return "***"
    return f"{compact[:3]}...{compact[-2:]}"

