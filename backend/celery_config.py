from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker='redis://127.0.0.1:6379/0',
        backend='redis://127.0.0.1:6379/0'
    )
    
    celery.conf.update(app.config)
    
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'tasks.send_daily_reminder',
            'schedule': crontab(hour=18, minute=0),
        },
        'send-daily-admin-report': {
            'task': 'tasks.send_daily_admin_report',
            'schedule': crontab(hour=8, minute=0),
        },
        'send-monthly-reports': {
            'task': 'tasks.send_monthly_report',
            'schedule': crontab(day_of_month=1, hour=0, minute=0),
        },
    }
    
    celery.conf.task_serializer = 'json'
    celery.conf.accept_content = ['json']
    celery.conf.result_serializer = 'json'
    celery.conf.timezone = 'UTC'
    celery.conf.enable_utc = True
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
