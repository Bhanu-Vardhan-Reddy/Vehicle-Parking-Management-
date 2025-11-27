"""
Celery Worker Entry Point
Run with: celery -A celery_worker.celery worker --loglevel=info --pool=solo
"""
from flask import Flask
from config import Config

# Create Flask app for Celery worker
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database with the worker app
from models import db, User, Role, ParkingLot, ParkingSpot, Booking
db.init_app(app)

# Create Celery instance
from celery_config import make_celery
celery = make_celery(app)

# Import tasks so Celery can discover them
import tasks

if __name__ == '__main__':
    celery.start()

