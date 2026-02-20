from celery import Celery

from app.core.config import settings

celery_app = Celery("slidenode", broker=settings.redis_dsn, backend=settings.redis_dsn)
celery_app.conf.update(task_track_started=True, task_serializer="json", result_serializer="json")
