import os
from celery import Celery
from celery.schedules import crontab

# Redis URL
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery app
celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks.scrape_tasks", "app.tasks.cleanup_tasks"],
)

# Config
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.conf.broker_connection_retry_on_startup = True
# Periodic task schedule
celery_app.conf.beat_schedule = {
    # Scrape every 6 hours
    "scrape-jobs-every-6-hours": {
        "task": "app.tasks.scrape_tasks.scrape_and_store_jobs",
        "schedule": crontab(minute=0, hour='*/6'),
        "args": ("job",),
    },
    # Delete old jobs once daily at 00:00 UTC
    "delete-old-jobs-daily": {
        "task": "app.tasks.cleanup_tasks.delete_old_jobs",
        "schedule": crontab(minute=0, hour=0),  # Every day at midnight UTC
    }
}

from app.tasks import scrape_tasks, cleanup_tasks
