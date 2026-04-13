"""Academic support agent that coordinates RAG answers for course spaces."""

from fahimni.agents.tutor_agent import TutorAgent
from fahimni.services.ai_service import AIService


class AcademicAgent:
    """Agent-style facade for RAG-backed Q&A."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        self._tutor = TutorAgent(ai_service or AIService())

    def answer_course_question(self, course_id: str, question: str) -> str:
        result = self._tutor.explain(course_id=course_id, question=question)
        return str(result["answer"])
