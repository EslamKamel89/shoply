from celery import Celery

from src.app.settings import settings

celery_app = Celery("shoply", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
import src.app.apps.auth.models
import src.app.apps.orders.models
import src.app.apps.products.models
import src.app.workers.products_tasks

"""
celery -A src.app.workers.celery_app worker --loglevel=info --pool=solo
"""
