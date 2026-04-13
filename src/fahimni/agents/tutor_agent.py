"""Tutor agent for step-by-step concept explanations over RAG context."""

from fahimni.services.ai_service import AIService


class TutorAgent:
    """Specialized teaching agent for explanatory responses."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai = ai_service or AIService()

    def explain(self, course_id: str, question: str) -> dict[str, object]:
        return self._ai.answer_with_rag(course_id=course_id, question=question, task_hint="tutor")
