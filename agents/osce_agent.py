from __future__ import annotations

from typing import Any

from agents.schemas import LectureChunk
from tools.lecture_tools import chunk_citation, split_sentences


class OSCEExaminerAgent:
    name = "OSCE Examiner Agent"

    def generate(
        self,
        chunks: list[LectureChunk],
        blueprint: dict[str, Any],
        count: int = 2,
        topic: str = "",
    ) -> list[dict[str, Any]]:
        topics = blueprint.get("clinical_conditions") or blueprint.get("main_topics") or [topic or "Lecture topic"]
        facts = blueprint.get("high_yield_facts") or self._fallback_facts(chunks)
        cases: list[dict[str, Any]] = []

        for index in range(max(1, count)):
            topic_label = topics[index % len(topics)]
            fact = facts[index % len(facts)]
            source = self._source_for_fact(fact, chunks)
            cases.append(
                {
                    "station_title": f"{topic_label} Oral Exam",
                    "stem": (
                        f"You are asked to assess a patient scenario related to {topic_label}. "
                        "Use only the provided lecture material to justify your answers."
                    ),
                    "examiner_questions": [
                        "What is the most important concept or diagnosis to consider?",
                        "Which lecture findings support your answer?",
                        "What initial investigations or assessment steps are relevant?",
                        "What management or follow-up points should be mentioned?",
                    ],
                    "expected_answers": [
                        fact,
                        "Answers should cite source-grounded lecture details rather than unsupported assumptions.",
                        "The student should identify red flags, key symptoms, or defining features when present.",
                    ],
                    "common_mistakes": [
                        "Giving patient-specific treatment advice beyond the lecture.",
                        "Listing generic facts without tying them to the station stem.",
                        "Missing the key high-yield fact from the source chunk.",
                    ],
                    "scoring_checklist": [
                        "Identifies the central topic or diagnosis.",
                        "Supports claims with lecture evidence.",
                        "Mentions relevant assessment or investigation points.",
                        "States management principles at an educational level.",
                        "Avoids unsupported or unsafe medical claims.",
                    ],
                    "source_chunks": [chunk_citation(source)] if source else [],
                }
            )
        return cases

    def _fallback_facts(self, chunks: list[LectureChunk]) -> list[str]:
        for chunk in chunks:
            sentences = split_sentences(chunk.text)
            if sentences:
                return sentences[:5]
        return ["No lecture facts were available."]

    def _source_for_fact(self, fact: str, chunks: list[LectureChunk]) -> LectureChunk | None:
        return next((chunk for chunk in chunks if fact[:40].lower() in chunk.text.lower()), chunks[0] if chunks else None)

