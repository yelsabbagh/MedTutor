from __future__ import annotations

from agents.schemas import LectureChunk
from tools.lecture_tools import list_topics, search_lecture


class LectureRetrievalAgent:
    name = "Lecture Retrieval Agent"

    def retrieve(self, chunks: list[LectureChunk], query: str, limit: int = 6) -> list[LectureChunk]:
        return search_lecture(chunks, query=query, limit=limit)

    def topics(self, chunks: list[LectureChunk], limit: int = 10) -> list[str]:
        return list_topics(chunks, limit=limit)

