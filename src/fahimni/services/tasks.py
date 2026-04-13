"""Celery tasks for background processing."""

from fahimni.core.celery_app import celery_app
from fahimni.services.ai_service import AIService


@celery_app.task(name="fahimni.tasks.healthcheck")  # type: ignore[untyped-decorator]
def healthcheck_task() -> str:
    """Simple task to verify the worker and broker wiring."""
    return "ok"


@celery_app.task(name="fahimni.tasks.ingest_course_text")  # type: ignore[untyped-decorator]
def ingest_course_text_task(course_id: str, content: str, source: str) -> int:
    """Background indexing task for large text uploads."""
    service = AIService()
    return service.ingest_text(course_id=course_id, content=content, source=source)


@celery_app.task(name="fahimni.tasks.generate_exam")  # type: ignore[untyped-decorator]
def generate_exam_task(course_id: str, topic: str, question_count: int) -> str:
    """Background exam generation task from indexed course materials."""
    service = AIService()
    return service.generate_exam(course_id=course_id, topic=topic, question_count=question_count)
