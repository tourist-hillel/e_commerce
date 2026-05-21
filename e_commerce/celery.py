import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from datetime import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_commerce.settings')

app = Celery('e_commerce')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# app.conf.timezone = timezone.utc
app.conf.beat_schedule = {
    'low-stock-check': {
        'task': 'shop.tasks.notify_low_stock_products',
        'schedule': crontab(minute='*/1')
    }
}
