"""Populate demo data and run an offline AI workflow smoke test."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.core.config import settings
from fahimni.core.security import hash_password
from fahimni.db.base import Base
from fahimni.db.repositories.course_repository import CourseRepository
from fahimni.db.repositories.material_repository import MaterialRepository
from fahimni.db.repositories.user_repository import UserRepository
from fahimni.db.session import AsyncSessionLocal, engine
from fahimni.models.archive_resource import ArchiveDifficulty, ArchiveResourceType
from fahimni.models.course import Course
from fahimni.models.course_material import MaterialSourceType, MaterialType
from fahimni.models.learning_event import LearningEventType
from fahimni.models.user import User, UserRole
from fahimni.services.ai_service import AIService

DEMO_PROFESSOR_EMAIL = "professor.demo@fahimni.com"
DEMO_STUDENT_EMAIL = "student.demo@fahimni.com"
DEMO_COURSE_CODE = "FAH-101"
DEMO_COURSE_TITLE = "Foundations of Algorithms"
DEMO_COURSE_TEXT = """
Recursion is a technique where a function calls itself to solve smaller instances of the same problem.
A recursion base case stops the repeated calls and prevents infinite loops.
Binary search is efficient because it halves the search space on every step.
Graphs model relationships between nodes and edges and are useful for dependency and network problems.
Breadth-first search visits nodes level by level, while depth-first search explores deeply before backtracking.
Dynamic programming stores overlapping subproblem results to avoid repeated work.
""".strip()


@dataclass(slots=True)
class WorkflowResult:
    course_id: str
    rag_answer: str
    search_hits: list[dict[str, object]]
    tutor_answer: str
    quiz_preview: str
    learning_path_days: int
    evaluation_score: int


class LocalHashEmbeddings:
    """Small deterministic embedding stub for offline demo and testing."""

    def __init__(self, dimensions: int = 48) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vectorize(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vectorize(text)

    def _vectorize(self, text: str) -> list[float]:
        tokens = re.findall(r"[A-Za-z0-9_]+", text.lower())
        vector = [0.0] * self.dimensions
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for index in range(self.dimensions):
                vector[index] += digest[index % len(digest)] / 255.0

        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class DemoAIService(AIService):
    """AI service variant that works offline with deterministic outputs."""

    def _initialize_runtime(self) -> None:
        if self._initialized:
            return
        self._embeddings = LocalHashEmbeddings()
        self._llm = None
        self._initialized = True

    def _generate_text(self, prompt: str) -> str:
        normalized = re.sub(r"\s+", " ", prompt).strip()
        lower = normalized.lower()

        if "summarize" in lower:
            return "Demo summary: recursion, search, graphs, and dynamic programming are the main ideas."
        if "mcq" in lower or "quiz" in lower:
            return "1. What is recursion? A. Self-referential problem solving. B. Sorting. C. Encryption. D. Compression."
        if "exam-style" in lower or "exam" in lower:
            return "Exam draft: 1) Define recursion. 2) Explain binary search. 3) Compare BFS and DFS."
        if "compare student answer" in lower:
            return "Score: 86/100. Improvement: add more precise technical vocabulary and mention the base case."
        if "generate 3 practice questions" in lower:
            return "1. Explain recursion. 2. Contrast BFS and DFS. 3. Why is binary search efficient?"
        if "learning path" in lower or "study plan" in lower:
            return "Day 1: Recursion. Day 2: Search. Day 3: Graphs. Day 4: Dynamic programming. Day 5: Mixed review."
        return "Demo AI response grounded in the seeded course content."


async def _get_or_create_user(
    repository: UserRepository,
    *,
    email: str,
    full_name: str,
    role: UserRole,
    password: str,
) -> User:
    existing = await repository.get_by_email(email)
    if existing is not None:
        return existing
    return await repository.create_user(
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=hash_password(password),
    )


async def _get_or_create_course(
    repository: CourseRepository,
    *,
    title: str,
    code: str,
    description: str,
    professor_id,
) -> Course:
    result = await repository.db.execute(select(Course).where(Course.code == code))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing
    return await repository.create_course(
        title=title,
        code=code,
        description=description,
        professor_id=professor_id,
    )


async def seed_demo_dataset(db: AsyncSession) -> dict[str, str | int]:
    """Create demo users, course data, materials, archive resources, and telemetry."""
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    material_repo = MaterialRepository(db)
    ai_service = DemoAIService()

    professor = await _get_or_create_user(
        user_repo,
        email=DEMO_PROFESSOR_EMAIL,
        full_name="Demo Professor",
        role=UserRole.PROFESSOR,
        password="demo-password",
    )
    student = await _get_or_create_user(
        user_repo,
        email=DEMO_STUDENT_EMAIL,
        full_name="Demo Student",
        role=UserRole.STUDENT,
        password="demo-password",
    )
    course = await _get_or_create_course(
        course_repo,
        title=DEMO_COURSE_TITLE,
        code=DEMO_COURSE_CODE,
        description="A demo course used to exercise the AI workflow against seeded content.",
        professor_id=professor.id,
    )

    from fahimni.models.enrollment import Enrollment

    existing_enrollment = await db.execute(
        select(Enrollment).where(
            Enrollment.course_id == course.id,
            Enrollment.student_id == student.id,
        )
    )
    if existing_enrollment.scalar_one_or_none() is None:
        await course_repo.enroll_student(course.id, student.id)

    summary_result = ai_service.teacher_upload_assistant(course_id=str(course.id), uploaded_text=DEMO_COURSE_TEXT)
    indexed_chunks = ai_service.ingest_text(
        course_id=str(course.id),
        content=DEMO_COURSE_TEXT,
        source="demo-seed-notes",
    )

    material = await material_repo.create_material(
        course_id=course.id,
        title="Demo Algorithm Notes",
        material_type=MaterialType.NOTES,
        source_type=MaterialSourceType.TEACHER,
        year=2026,
        is_verified=True,
        storage_url="demo://algorithm-notes",
        created_by=professor.id,
    )
    archive = await material_repo.create_archive_resource(
        course_id=course.id,
        title="Demo Midterm 2025",
        resource_type=ArchiveResourceType.EXAM,
        year=2025,
        university="Fahimni University",
        professor="Demo Professor",
        difficulty=ArchiveDifficulty.MEDIUM,
        file_url="demo://midterm-2025.pdf",
        material_id=material.id,
        created_by=professor.id,
    )
    await material_repo.track_event(
        user_id=student.id,
        course_id=course.id,
        event_type=LearningEventType.QUESTION_ASKED,
        topic="recursion",
        payload={"question": "What is recursion?"},
    )
    await material_repo.upsert_progress(
        user_id=student.id,
        course_id=course.id,
        topic="recursion",
        mastery_score=72.5,
    )

    await db.commit()

    return {
        "professor_id": str(professor.id),
        "student_id": str(student.id),
        "course_id": str(course.id),
        "course_code": course.code,
        "material_id": str(material.id),
        "archive_id": str(archive.id),
        "indexed_chunks": indexed_chunks,
        "summary_preview": str(summary_result.get("summary", ""))[:140],
    }


async def run_demo_ai_smoke(course_id: str, student_id: str) -> WorkflowResult:
    """Run the main AI workflow against the seeded course content."""
    ai_service = DemoAIService()
    rag_result = ai_service.answer_with_rag(course_id=course_id, question="Explain recursion in simple terms.")
    search_hits = ai_service.hybrid_search(course_id=course_id, query="recursion and binary search", k=3)
    workflow = ai_service.run_multi_agent_workflow(
        course_id=course_id,
        question="Explain recursion in simple terms.",
        student_id=student_id,
    )
    learning_path = ai_service.generate_learning_path(
        weak_topics=["recursion", "binary search"],
        study_minutes_per_day=45,
        horizon_days=5,
    )
    evaluation = ai_service.evaluate_student_answer(
        reference="Recursion is a function that calls itself and must have a base case.",
        student_answer="Recursion is a function calling itself and stopping at a base case.",
    )

    return WorkflowResult(
        course_id=course_id,
        rag_answer=str(rag_result["answer"]),
        search_hits=[{
            "text": hit.text,
            "source": hit.source,
            "score": hit.score,
            "page": hit.page,
            "highlight": hit.highlight,
        } for hit in search_hits],
        tutor_answer=str(workflow["tutor_agent"]["answer"]),
        quiz_preview=str(workflow["quiz_agent"])[:180],
        learning_path_days=len(learning_path["plan"]),
        evaluation_score=int(evaluation["score"]),
    )


async def _main_async(vector_store_path: str | None = None) -> None:
    if vector_store_path:
        settings.vector_store_path = vector_store_path

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        seed = await seed_demo_dataset(db)

    result = await run_demo_ai_smoke(seed["course_id"], seed["student_id"])
    output: dict[str, Any] = {
        "seed": seed,
        "smoke": {
            "course_id": result.course_id,
            "rag_answer": result.rag_answer,
            "search_hits": result.search_hits,
            "tutor_answer": result.tutor_answer,
            "quiz_preview": result.quiz_preview,
            "learning_path_days": result.learning_path_days,
            "evaluation_score": result.evaluation_score,
        },
    }
    print(json.dumps(output, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate demo data and run the AI smoke workflow.")
    parser.add_argument(
        "--vector-store-path",
        default=None,
        help="Optional vector store directory. Defaults to the configured path.",
    )
    args = parser.parse_args()
    asyncio.run(_main_async(args.vector_store_path))


if __name__ == "__main__":
    main()
