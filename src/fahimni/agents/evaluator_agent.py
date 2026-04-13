"""Evaluator agent for answer grading and feedback generation."""

from fahimni.services.ai_service import AIService


class EvaluatorAgent:
    """Agent that scores student free-text answers."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai = ai_service or AIService()

    def evaluate(self, reference_answer: str, student_answer: str) -> dict[str, object]:
        return self._ai.evaluate_student_answer(reference=reference_answer, student_answer=student_answer)
