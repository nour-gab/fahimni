"""Quiz agent for MCQ/exercise generation from indexed course content."""

from fahimni.services.ai_service import AIService


class QuizAgent:
    """Agent that generates quizzes and exam simulations."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai = ai_service or AIService()

    def generate_exam(self, course_id: str, topic: str, question_count: int = 5) -> str:
        return self._ai.generate_exam(course_id=course_id, topic=topic, question_count=question_count)

    def generate_practice(self, prompt: str) -> str:
        return self._ai._generate_text(f"Generate 5 practice questions about: {prompt}")
