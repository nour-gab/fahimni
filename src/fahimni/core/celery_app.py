"""Celery application instance for background AI task processing."""

from celery import Celery  # type: ignore[import-untyped]

from fahimni.core.config import settings

celery_app = Celery(
    "fahimni",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["fahimni.services.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)