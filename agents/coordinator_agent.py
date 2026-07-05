from __future__ import annotations

import json
from typing import Any

from agents.blueprint_agent import ExamBlueprintAgent
from agents.export_agent import ExportAgent
from agents.mcq_agent import MCQGeneratorAgent
from agents.osce_agent import OSCEExaminerAgent
from agents.retrieval_agent import LectureRetrievalAgent
from agents.schemas import LectureChunk, WorkflowResult
from agents.validator_agent import MedicalSafetyValidatorAgent
from tools.lecture_tools import chunk_pages, chunk_text, extract_text_from_pdf


class CoordinatorAgent:
    name = "Coordinator Agent"

    def __init__(self) -> None:
        self.retrieval_agent = LectureRetrievalAgent()
        self.blueprint_agent = ExamBlueprintAgent()
        self.mcq_agent = MCQGeneratorAgent()
        self.osce_agent = OSCEExaminerAgent()
        self.validator_agent = MedicalSafetyValidatorAgent()
        self.export_agent = ExportAgent()

    def run(
        self,
        task: str,
        lecture_text: str = "",
        pdf_bytes: bytes | None = None,
        source_name: str = "lecture",
        topic: str = "",
        count: int = 5,
        existing_mcqs_json: str = "",
    ) -> WorkflowResult:
        normalized_task = task.lower().strip()
        result = WorkflowResult(task=normalized_task)
        result.add_trace(self.name, "route", f"Selected {normalized_task} workflow.")

        chunks = self._load_chunks(lecture_text=lecture_text, pdf_bytes=pdf_bytes, source_name=source_name)
        result.chunks = chunks
        result.add_trace("MCP Tool Server", "chunk", f"Prepared {len(chunks)} lecture chunks.")

        source_text = "\n".join(chunk.text for chunk in chunks) or lecture_text or existing_mcqs_json
        result.safety = self.validator_agent.validate_input(source_text)
        result.add_trace(
            self.validator_agent.name,
            "input safety",
            self._safety_detail(result.safety),
            "warning" if not result.safety.get("safe", True) else "ok",
        )

        if normalized_task == "validate":
            result.mcqs = self._parse_existing_mcqs(existing_mcqs_json)
            result.validation = self.validator_agent.validate_mcqs(result.mcqs, chunks)
            result.add_trace(
                self.validator_agent.name,
                "validate",
                f"Validated {len(result.mcqs)} existing MCQs.",
                "ok" if result.validation.get("valid") else "warning",
            )
            result.exports = self.export_agent.export_mcqs(result.mcqs)
            result.add_trace(self.export_agent.name, "export", "Created validation-ready MCQ exports.")
            return result

        query = topic or normalized_task
        result.retrieved_chunks = self.retrieval_agent.retrieve(chunks, query=query, limit=6)
        result.add_trace(
            self.retrieval_agent.name,
            "retrieve",
            f"Found {len(result.retrieved_chunks)} relevant chunks for '{query}'.",
        )

        result.blueprint = self.blueprint_agent.build(result.retrieved_chunks or chunks)
        result.add_trace(
            self.blueprint_agent.name,
            "blueprint",
            f"Mapped {len(result.blueprint.get('main_topics', []))} main topics.",
        )

        if normalized_task in {"mcq", "mcqs", "generate mcqs"}:
            result.mcqs = self.mcq_agent.generate(
                result.retrieved_chunks or chunks,
                result.blueprint,
                count=count,
                topic=topic,
            )
            result.add_trace(self.mcq_agent.name, "generate", f"Generated {len(result.mcqs)} MCQs.")
            result.validation = self.validator_agent.validate_mcqs(result.mcqs, result.retrieved_chunks or chunks)
            result.mcqs = self.validator_agent.repair_mcqs(result.mcqs, result.validation)
            result.add_trace(
                self.validator_agent.name,
                "validate",
                result.validation.get("summary", "Validation complete."),
                "ok" if result.validation.get("valid") else "warning",
            )
            result.exports = self.export_agent.export_mcqs(result.mcqs)
            result.add_trace(self.export_agent.name, "export", "Created JSON, Markdown, and CSV files.")
            return result

        if normalized_task in {"osce", "osce cases", "oral exam"}:
            result.osce_cases = self.osce_agent.generate(
                result.retrieved_chunks or chunks,
                result.blueprint,
                count=max(1, min(count, 5)),
                topic=topic,
            )
            result.add_trace(self.osce_agent.name, "generate", f"Generated {len(result.osce_cases)} OSCE cases.")
            result.exports = self.export_agent.export_osce(result.osce_cases)
            result.add_trace(self.export_agent.name, "export", "Created OSCE JSON and Markdown files.")
            return result

        result.exports = self.export_agent.export_blueprint(result.blueprint)
        result.add_trace(self.export_agent.name, "export", "Created study blueprint files.")
        return result

    def _load_chunks(
        self,
        lecture_text: str,
        pdf_bytes: bytes | None,
        source_name: str,
    ) -> list[LectureChunk]:
        if pdf_bytes:
            pages = extract_text_from_pdf(pdf_bytes)
            return chunk_pages(pages, source=source_name)
        return chunk_text(lecture_text, source=source_name)

    def _parse_existing_mcqs(self, existing_mcqs_json: str) -> list[dict[str, Any]]:
        if not existing_mcqs_json.strip():
            return []
        parsed = json.loads(existing_mcqs_json)
        if isinstance(parsed, dict) and "mcqs" in parsed:
            parsed = parsed["mcqs"]
        if isinstance(parsed, dict):
            parsed = [parsed]
        if not isinstance(parsed, list):
            raise ValueError("Existing MCQs must be a JSON object, a list, or an object with an 'mcqs' list.")
        return [item for item in parsed if isinstance(item, dict)]

    def _safety_detail(self, safety: dict[str, Any]) -> str:
        details: list[str] = []
        injection = safety.get("prompt_injection", {})
        phi = safety.get("phi", {})
        if injection.get("risk") != "none":
            details.append(f"Prompt-injection risk: {', '.join(injection.get('matches', []))}")
        if phi.get("risk") != "none":
            details.append(f"Possible PHI findings: {len(phi.get('findings', []))}")
        return "; ".join(details) if details else "No obvious prompt-injection or PHI patterns detected."
