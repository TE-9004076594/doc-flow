"""Celery worker configuration for async tasks."""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "doc_flow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def debug_task(self):
    """Simple debug task to verify Celery is working."""
    return {"status": "ok", "task_id": self.request.id}
