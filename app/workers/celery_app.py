# app/workers/celery_app.py

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "upflow",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)

import app.workers.assemble
