"""
Celery application for background tasks.
"""

from celery import Celery

from app.core import settings

celery_app = Celery(
    "sitebuilder",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

# Auto-discover tasks in app.tasks package
celery_app.autodiscover_tasks(["app.tasks"])

# Import tasks to ensure they're registered
from app.tasks.publish import publish_site_task  # noqa: F401, E402

__all__ = ["celery_app", "publish_site_task"]
