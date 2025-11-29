from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from models import db, User, Role, ParkingLot, ParkingSpot, Booking
db.init_app(app)

from celery_config import make_celery
celery = make_celery(app)

import tasks

if __name__ == '__main__':
    celery.start()
