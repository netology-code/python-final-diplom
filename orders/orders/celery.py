import os

import celery 


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders")
# app = celery.Celery('orders', backend=os.getenv('CELERY_BACKEND'), broker=os.getenv('CELERY_BROKER'))
app = celery.Celery("orders")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()