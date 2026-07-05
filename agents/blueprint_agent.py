from __future__ import annotations

from collections import Counter
from typing import Any

from agents.schemas import LectureChunk
from tools.lecture_tools import list_topics, split_sentences, tokenize


ANGLE_KEYWORDS = {
    "diagnosis": "Diagnosis and diagnostic clues",
    "treatment": "Initial management and treatment choices",
    "management": "Initial management and treatment choices",
    "risk": "Risk factors and prevention",
    "complication": "Complications and red flags",
    "symptom": "Presentation and symptom pattern",
    "investigation": "Investigations and interpretation",
}


class ExamBlueprintAgent:
    name = "Exam Blueprint Agent"

    def build(self, chunks: list[LectureChunk]) -> dict[str, Any]:
        text = "\n".join(chunk.text for chunk in chunks)
        topics = list_topics(chunks, limit=8)
        sentences = split_sentences(text)
        high_yield = self._high_yield_sentences(sentences)
        angles = self._exam_angles(text)
        conditions = self._clinical_conditions(sentences, topics)

        return {
            "main_topics": topics,
            "high_yield_facts": high_yield[:10],
            "clinical_conditions": conditions[:8],
            "possible_exam_angles": angles,
            "difficulty_distribution": {"easy": 20, "moderate": 60, "hard": 20},
        }

    def _high_yield_sentences(self, sentences: list[str]) -> list[str]:
        priority_terms = {
            "diagnosis",
            "management",
            "treatment",
            "cause",
            "risk",
            "feature",
            "symptom",
            "sign",
            "investigation",
            "complication",
            "characterized",
            "defined",
        }
        scored: list[tuple[int, str]] = []
        for sentence in sentences:
            tokens = set(tokenize(sentence))
            score = len(tokens & priority_terms)
            if score:
                scored.append((score, sentence))
        scored.sort(key=lambda item: (-item[0], len(item[1])))
        return [sentence for _, sentence in scored] or sentences[:10]

    def _exam_angles(self, text: str) -> list[str]:
        tokens = set(tokenize(text))
        angles = [label for keyword, label in ANGLE_KEYWORDS.items() if keyword in tokens]
        if "Presentation and symptom pattern" not in angles:
            angles.append("Presentation and symptom pattern")
        if "Source-grounded explanation of core facts" not in angles:
            angles.append("Source-grounded explanation of core facts")
        return list(dict.fromkeys(angles))[:8]

    def _clinical_conditions(self, sentences: list[str], topics: list[str]) -> list[str]:
        candidates = Counter()
        for sentence in sentences:
            for phrase in topics:
                if phrase.lower() in sentence.lower():
                    candidates[phrase] += 1
        return [item for item, _ in candidates.most_common()] or topics[:6]

