from celery import Celery

from app.core.config import settings

celery_app = Celery("mts_fds", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_default_queue = "mts_fds"
