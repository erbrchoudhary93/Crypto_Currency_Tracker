from __future__ import absolute_import ,unicode_literals
import os
from celery import Celery
from django.conf import settings




# from celery.schedules import crontab
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
os.environ.setdefault('DJANGO_SETTINGS_MODULE','crypto_app.settings')

app=Celery('crypto_app')


# celery beat settings
app.conf.beat_schedule = {
    'add-every-58-seconds': {
        'task': 'app.task.get_crypto_data',
        'schedule': 58.0,
       
    },
}


app.conf.enable_utc =False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object(settings,namespace='CELERY')


#




app.autodiscover_tasks()

# # load task from all registerd django app config


@app.task(bind=True)
def debug_task(self):
    print(f'Request : {self.request!r}')
    
 