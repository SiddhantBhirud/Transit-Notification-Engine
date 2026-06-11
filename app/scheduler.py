from celery.schedules import crontab
from app.tasks import celery_app

celery_app.conf.beat_schedule = {
    "poll-transit-feed-every-30-seconds": {
        "task": "tasks.poll_transit_feed",
        "schedule": 30.0,  # seconds
    },
}

celery_app.conf.timezone = "UTC"