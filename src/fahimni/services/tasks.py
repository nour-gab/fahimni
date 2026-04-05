"""Celery tasks for background processing."""

from fahimni.core.celery_app import celery_app


@celery_app.task(name="fahimni.tasks.healthcheck")  # type: ignore[untyped-decorator]
def healthcheck_task() -> str:
    """Simple task to verify the worker and broker wiring."""
    return "ok"
