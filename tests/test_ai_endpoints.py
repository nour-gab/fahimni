"""API tests for AI endpoints with service mocking."""

import pytest
from httpx import AsyncClient

from fahimni.api.v1.ai import get_ai_service
from fahimni.core.dependencies import get_current_user
from fahimni.main import app


class MockAIService:
    """Lightweight test double for AI endpoints."""

    def answer_with_rag(self, course_id: str, question: str, task_hint: str = "") -> dict[str, object]:
        return {
            "answer": f"Mock answer for {question}",
            "sources": [{"source": "mock.pdf", "score": 1.0}],
        }

    def hybrid_search(self, course_id: str, query: str, k: int = 5) -> list[object]:
        class Hit:
            def __init__(self) -> None:
                self.__dict__ = {"text": "Recursion is ...", "source": "notes", "score": 0.98}

        return [Hit()]


class MockUser:
    id = "00000000-0000-0000-0000-000000000000"
    role = "PROFESSOR"
    is_active = True


@pytest.mark.asyncio
async def test_ai_rag_ask_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ai/rag/ask",
        json={"course_id": "course-1", "question": "What is recursion?"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ai_rag_ask_with_dependency_override(client: AsyncClient) -> None:
    app.dependency_overrides[get_ai_service] = lambda: MockAIService()
    app.dependency_overrides[get_current_user] = lambda: MockUser()
    try:
        response = await client.post(
            "/api/v1/ai/rag/ask",
            json={"course_id": "course-1", "question": "What is recursion?"},
        )
        assert response.status_code == 200
        assert response.json()["answer"] == "Mock answer for What is recursion?"
    finally:
        app.dependency_overrides.clear()
