import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handwriting_project.settings')

app = Celery('handwriting_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
