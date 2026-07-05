from __future__ import annotations

from typing import Any

from agents.schemas import LectureChunk
from tools.lecture_tools import chunk_citation, split_sentences


GENERIC_DISTRACTORS = [
    "It is best confirmed only by a single nonspecific symptom.",
    "It usually requires ignoring the lecture source and using unrelated assumptions.",
    "It is always benign and does not require structured assessment.",
    "It is defined by a finding that is not supported in the provided lecture.",
]


class MCQGeneratorAgent:
    name = "MCQ Generator Agent"

    def generate(
        self,
        chunks: list[LectureChunk],
        blueprint: dict[str, Any],
        count: int = 5,
        topic: str = "",
    ) -> list[dict[str, Any]]:
        facts = self._candidate_facts(chunks, blueprint)
        topics = blueprint.get("main_topics") or ["the lecture topic"]
        mcqs: list[dict[str, Any]] = []

        for index in range(max(1, count)):
            fact, chunk = facts[index % len(facts)]
            topic_label = self._topic_for_fact(fact, topics, fallback=topic or "the lecture")
            correct_label = ["B", "C", "D", "A", "E"][index % 5]
            options = self._build_options(fact, correct_label)
            mcqs.append(
                {
                    "id": f"mcq_{index + 1:03d}",
                    "question": (
                        f"A medical student is reviewing {topic_label}. "
                        "Which option is best supported by the provided lecture?"
                    ),
                    "options": options,
                    "correct_answer": correct_label,
                    "explanations": self._explanations(options, correct_label, fact),
                    "source_chunks": [chunk_citation(chunk)],
                    "difficulty": "moderate" if index % 3 else "easy",
                }
            )

        return mcqs

    def _candidate_facts(
        self, chunks: list[LectureChunk], blueprint: dict[str, Any]
    ) -> list[tuple[str, LectureChunk]]:
        high_yield = blueprint.get("high_yield_facts") or []
        candidates: list[tuple[str, LectureChunk]] = []
        for fact in high_yield:
            matched_chunk = next((chunk for chunk in chunks if fact[:40].lower() in chunk.text.lower()), None)
            if matched_chunk:
                candidates.append((fact, matched_chunk))

        if candidates:
            return candidates

        for chunk in chunks:
            for sentence in split_sentences(chunk.text):
                candidates.append((sentence, chunk))

        if candidates:
            return candidates

        placeholder = LectureChunk("chunk_000", "empty", None, "No lecture content was provided.")
        return [("No lecture content was provided.", placeholder)]

    def _topic_for_fact(self, fact: str, topics: list[str], fallback: str) -> str:
        fact_lower = fact.lower()
        for topic in topics:
            if topic.lower() in fact_lower:
                return topic
        return fallback or topics[0]

    def _build_options(self, fact: str, correct_label: str) -> list[dict[str, str]]:
        labels = ["A", "B", "C", "D", "E"]
        distractors = self._distractors_for_fact(fact)
        options: list[dict[str, str]] = []
        distractor_index = 0
        for label in labels:
            if label == correct_label:
                text = fact
            else:
                text = distractors[distractor_index % len(distractors)]
                distractor_index += 1
            options.append({"label": label, "text": text})
        return options

    def _distractors_for_fact(self, fact: str) -> list[str]:
        compact = fact.rstrip(".")
        distractors = [
            f"{compact}, but this is unrelated to exam preparation.",
            "The lecture states the opposite of this key point.",
            "The main issue is excluded because it is never clinically relevant.",
            "The safest answer is to choose an unsupported diagnosis without source evidence.",
        ]
        return distractors + GENERIC_DISTRACTORS

    def _explanations(
        self, options: list[dict[str, str]], correct_label: str, fact: str
    ) -> dict[str, str]:
        explanations: dict[str, str] = {}
        for option in options:
            label = option["label"]
            if label == correct_label:
                explanations[label] = f"Correct. This option is directly grounded in the lecture: {fact}"
            else:
                explanations[label] = (
                    "Incorrect. This distractor is not supported by the retrieved lecture evidence."
                )
        return explanations

