from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backendapis.settings')

app = Celery('backendapis')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'delete-expired-files': {
        'task': 'tempupload.tasks.delete_expired_files_task',
        'schedule': crontab(minute=0, hour=0),  # Every day
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
