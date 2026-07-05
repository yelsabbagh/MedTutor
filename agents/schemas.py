from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


MEDICAL_DISCLAIMER = (
    "This tool is for medical education and exam preparation only. "
    "It does not provide diagnosis, treatment, or patient-specific medical advice."
)


@dataclass(frozen=True)
class LectureChunk:
    chunk_id: str
    source: str
    page: int | None
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentTraceStep:
    agent: str
    action: str
    detail: str
    status: str = "ok"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class WorkflowResult:
    task: str
    disclaimer: str = MEDICAL_DISCLAIMER
    trace: list[AgentTraceStep] = field(default_factory=list)
    safety: dict[str, Any] = field(default_factory=dict)
    chunks: list[LectureChunk] = field(default_factory=list)
    retrieved_chunks: list[LectureChunk] = field(default_factory=list)
    blueprint: dict[str, Any] = field(default_factory=dict)
    mcqs: list[dict[str, Any]] = field(default_factory=list)
    osce_cases: list[dict[str, Any]] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    exports: dict[str, str] = field(default_factory=dict)

    def add_trace(self, agent: str, action: str, detail: str, status: str = "ok") -> None:
        self.trace.append(AgentTraceStep(agent=agent, action=action, detail=detail, status=status))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["trace"] = [step.to_dict() for step in self.trace]
        data["chunks"] = [chunk.to_dict() for chunk in self.chunks]
        data["retrieved_chunks"] = [chunk.to_dict() for chunk in self.retrieved_chunks]
        return data

