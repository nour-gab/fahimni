"""Orchestrator agent that coordinates all specialized learning agents."""

from fahimni.agents.evaluator_agent import EvaluatorAgent
from fahimni.agents.planner_agent import PlannerAgent
from fahimni.agents.quiz_agent import QuizAgent
from fahimni.agents.search_agent import SearchAgent
from fahimni.agents.tutor_agent import TutorAgent
from fahimni.services.ai_service import AIService


class OrchestratorAgent:
    """Coordinator for tutor, search, quiz, planner, and evaluator flows."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        shared = ai_service or AIService()
        self.tutor = TutorAgent(shared)
        self.search = SearchAgent(shared)
        self.quiz = QuizAgent(shared)
        self.planner = PlannerAgent(shared)
        self.evaluator = EvaluatorAgent(shared)

    def run(self, course_id: str, prompt: str, student_id: str) -> dict[str, object]:
        search_hits = self.search.search(course_id=course_id, query=prompt, k=4)
        return {
            "student_id": student_id,
            "tutor_agent": self.tutor.explain(course_id=course_id, question=prompt),
            "search_agent": [
                {"text": hit.text, "source": hit.source, "score": hit.score}
                for hit in search_hits
            ],
            "quiz_agent": self.quiz.generate_practice(prompt),
            "planner_agent": self.planner.build_plan([prompt], 60, 5),
        }
