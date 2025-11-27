"""
Celery Configuration
Milestone 8: Background Jobs
"""
from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    """Create Celery instance with Flask app context."""
    # Create Celery with direct broker/backend URLs
    celery = Celery(
        app.import_name,
        broker='redis://127.0.0.1:6379/0',
        backend='redis://127.0.0.1:6379/0'
    )
    
    # Update configuration from Flask app
    celery.conf.update(app.config)
    
    # Configure periodic tasks (new format)
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'tasks.send_daily_reminder',
            'schedule': crontab(hour=18, minute=0),  # 6:00 PM daily
        },
        'send-daily-admin-report': {
            'task': 'tasks.send_daily_admin_report',
            'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
        },
        'send-monthly-reports': {
            'task': 'tasks.send_monthly_report',
            'schedule': crontab(day_of_month=1, hour=0, minute=0),  # 12:00 AM on 1st
        },
    }
    
    # Ensure using new format consistently
    celery.conf.task_serializer = 'json'
    celery.conf.accept_content = ['json']
    celery.conf.result_serializer = 'json'
    celery.conf.timezone = 'UTC'
    celery.conf.enable_utc = True
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

