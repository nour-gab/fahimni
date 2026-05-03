"""Smoke test for demo dataset seeding and offline AI workflow execution."""

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fahimni.db.base import Base
from fahimni.core.config import settings
from fahimni.scripts.demo_workflow import run_demo_ai_smoke, seed_demo_dataset


SMOKE_DATABASE_URL = "postgresql+asyncpg://fahimni:fahimni@localhost:5433/postgres"


@pytest.mark.asyncio
async def test_demo_dataset_and_ai_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vector_store_path = tmp_path / "chroma-demo"
    monkeypatch.setattr(settings, "vector_store_path", str(vector_store_path), raising=False)

    engine = create_async_engine(SMOKE_DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db_session:
        seed = await seed_demo_dataset(db_session)
    result = await run_demo_ai_smoke(seed["course_id"], seed["student_id"])

    await engine.dispose()

    assert seed["course_code"] == "FAH-101"
    assert seed["indexed_chunks"] > 0
    assert seed["material_id"]
    assert seed["archive_id"]
    assert result.course_id == seed["course_id"]
    assert result.rag_answer
    assert result.search_hits
    assert result.tutor_answer
    assert result.quiz_preview
    assert result.learning_path_days == 5
    assert result.evaluation_score > 0
