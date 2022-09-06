import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hungry_backend_api.settings.dev')

celery = Celery('hungry_backend')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()