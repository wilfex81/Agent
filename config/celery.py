import os
from celery import Celery
from celery.schedules import crontab
from django.apps import apps

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

celery_app = Celery("config")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

# Define Celery Beat Scheduled Tasks
celery_app.conf.beat_schedule = {
    "check_scheduled_rides": {
        "task": "agent.tasks.assign_scheduled_rides",  # Ensure correct path
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "cancel_unconfirmed_rides": {
        "task": "agent.tasks.auto_cancel_unconfirmed_rides",  # Ensure correct path
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
