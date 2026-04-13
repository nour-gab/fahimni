"""Unit tests for standalone agent files with mock AI service."""

from __future__ import annotations

from typing import Any

from fahimni.agents.evaluator_agent import EvaluatorAgent
from fahimni.agents.ocr_agent import OCRAgent
from fahimni.agents.orchestrator_agent import OrchestratorAgent
from fahimni.agents.planner_agent import PlannerAgent
from fahimni.agents.quiz_agent import QuizAgent
from fahimni.agents.search_agent import SearchAgent
from fahimni.agents.tutor_agent import TutorAgent
from fahimni.services.ai_service import SearchHit


class FakeAIService:
    """Minimal service stub used for agent-level tests."""

    def answer_with_rag(self, course_id: str, question: str, task_hint: str = "") -> dict[str, object]:
        return {"answer": f"{task_hint}:{question}", "sources": []}

    def generate_exam(self, course_id: str, topic: str, question_count: int) -> str:
        return f"exam-{course_id}-{topic}-{question_count}"

    def _generate_text(self, prompt: str) -> str:
        return f"generated:{prompt}"

    def hybrid_search(self, course_id: str, query: str, k: int = 5) -> list[SearchHit]:
        return [SearchHit(text="snippet", source="source.pdf", score=0.9)]

    def generate_learning_path(
        self,
        weak_topics: list[str],
        study_minutes_per_day: int,
        horizon_days: int,
    ) -> dict[str, Any]:
        return {"plan": [{"focus": weak_topics[0], "days": horizon_days, "minutes": study_minutes_per_day}]}

    def ingest_ocr_image(self, course_id: str, image_bytes: bytes, filename: str) -> dict[str, object]:
        return {"chunks": 2, "detected": {"equations": True}}

    def evaluate_student_answer(self, reference: str, student_answer: str) -> dict[str, object]:
        return {"score": 88, "feedback": "good"}


def test_tutor_agent() -> None:
    agent = TutorAgent(FakeAIService())
    result = agent.explain("c1", "Explain recursion")
    assert result["answer"] == "tutor:Explain recursion"


def test_quiz_agent() -> None:
    agent = QuizAgent(FakeAIService())
    assert agent.generate_exam("c1", "recursion", 3) == "exam-c1-recursion-3"


def test_search_agent() -> None:
    agent = SearchAgent(FakeAIService())
    hits = agent.search("c1", "find recursion", k=1)
    assert len(hits) == 1
    assert hits[0].source == "source.pdf"


def test_planner_agent() -> None:
    agent = PlannerAgent(FakeAIService())
    result = agent.build_plan(["recursion"], 45, 5)
    assert "plan" in result


def test_ocr_agent() -> None:
    agent = OCRAgent(FakeAIService())
    result = agent.process_image("c1", b"fake", "scan.png")
    assert result["chunks"] == 2


def test_evaluator_agent() -> None:
    agent = EvaluatorAgent(FakeAIService())
    result = agent.evaluate("ref", "answer")
    assert result["score"] == 88


def test_orchestrator_agent() -> None:
    agent = OrchestratorAgent(FakeAIService())
    result = agent.run(course_id="c1", prompt="recursion", student_id="s1")
    assert result["student_id"] == "s1"
    assert "tutor_agent" in result
    assert "search_agent" in result
