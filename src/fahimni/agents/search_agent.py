"""Search agent implementing hybrid semantic + BM25 retrieval."""

from fahimni.services.ai_service import AIService, SearchHit


class SearchAgent:
    """Agent dedicated to source-grounded snippet retrieval."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai = ai_service or AIService()

    def search(self, course_id: str, query: str, k: int = 5) -> list[SearchHit]:
        return self._ai.hybrid_search(course_id=course_id, query=query, k=k)
