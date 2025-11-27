# 🔧 Vehicle Parking System - Backend

Flask REST API backend for the Vehicle Parking Management System with Celery task queue for automated email notifications.

## 📋 Overview

RESTful API providing:
- User authentication with JWT tokens
- Role-based access control (Admin/User)
- CRUD operations for parking lots and spots
- Booking management system
- Automated email notifications via Celery
- CSV data export capabilities

---

## 🚀 Quick Start

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize database
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()

# Run Flask server
python app.py

# In separate terminals:
# Terminal 2 - Start Celery Worker
celery -A celery_worker.celery worker --loglevel=info --pool=solo

# Terminal 3 - Start Celery Beat
celery -A celery_worker.celery beat --loglevel=info
```

---

## 📁 File Structure

```
backend/
├── app.py                   # Flask application entry point
├── models.py                # Database models (SQLAlchemy)
├── routes.py                # API endpoints and route handlers
├── config.py                # Configuration settings
├── tasks.py                 # Celery background tasks
├── celery_config.py         # Celery and Beat configuration
├── celery_worker.py         # Celery worker initialization
├── asynctask_demo.py        # Email system testing script
├── requirements.txt         # Python dependencies
└── instance/
    └── parking.db           # SQLite database file
```

---

## 🗃️ Core Files Explained

### 1. `app.py` - Application Entry Point

**Purpose**: Initialize and configure the Flask application

**Key Components**:
- Flask app creation
- Database initialization
- Flask-Security setup
- CORS configuration
- Admin user seeding
- Route registration

**Code Highlights**:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
CORS(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create admin user on startup
with app.app_context():
    db.create_all()
    if not user_datastore.find_user(email="admin@parking.com"):
        user_datastore.create_user(
            email="admin@parking.com",
            password=hash_password("admin123"),
            roles=['admin']
        )
```

**Environment**:
- Port: 5000
- Debug: True (development)
- Database: SQLite

---

### 2. `models.py` - Database Models

**Purpose**: Define database schema using SQLAlchemy ORM

**Models**:

#### User Model
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    
    @property
    def active(self):
        return True  # All users are active
    
    roles = db.relationship('Role', secondary=roles_users)
    bookings = db.relationship('Booking', backref='user', cascade='all, delete-orphan')
```

#### ParkingLot Model
```python
class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    
    spots = db.relationship('ParkingSpot', backref='lot', cascade='all, delete-orphan')
```

#### ParkingSpot Model
```python
class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Available')  # Available/Occupied
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'))
    
    bookings = db.relationship('Booking', backref='spot')
```

#### Booking Model
```python
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'))
    booking_type = db.Column(db.String(20), default='instant')  # instant/reserved
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    reserved_start = db.Column(db.DateTime)
    reserved_end = db.Column(db.DateTime)
    total_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Active')  # Active/Completed/Cancelled
```

---

### 3. `routes.py` - API Endpoints

**Purpose**: Define all RESTful API endpoints

**Route Categories**:

#### Authentication Routes
```python
@app.route('/auth/register', methods=['POST'])
def register():
    # Register new user with 'user' role
    # Returns: { user, token }

@app.route('/auth/login', methods=['POST'])
def login():
    # Authenticate user and return JWT token
    # Returns: { token, user, roles }
```

#### Parking Lot Routes
```python
@app.route('/api/lots', methods=['GET'])
@auth_required
def get_lots():
    # Get all parking lots with availability

@app.route('/api/lots', methods=['POST'])
@auth_required
@roles_required('admin')
def create_lot():
    # Create new lot and auto-generate spots

@app.route('/api/lots/<int:lot_id>', methods=['PUT'])
@auth_required
@roles_required('admin')
def update_lot(lot_id):
    # Update lot and adjust spot count

@app.route('/api/lots/<int:lot_id>', methods=['DELETE'])
@auth_required
@roles_required('admin')
def delete_lot(lot_id):
    # Delete lot (only if no occupied spots)
```

#### Booking Routes
```python
@app.route('/api/book', methods=['POST'])
@auth_required
def book_spot():
    # Book parking spot (instant or reserved)
    # Triggers: send_booking_confirmation task

@app.route('/api/release/<int:booking_id>', methods=['POST'])
@auth_required
def release_spot(booking_id):
    # Release spot and calculate final cost

@app.route('/api/bookings', methods=['GET'])
@auth_required
def get_bookings():
    # Get user's booking history
```

#### Admin Routes
```python
@app.route('/api/users', methods=['GET'])
@auth_required
@roles_required('admin')
def get_users():
    # Get all registered users with stats

@app.route('/api/admin/send-daily-reminder', methods=['POST'])
@auth_required
@roles_required('admin')
def trigger_daily_reminder():
    # Manually trigger daily reminders

@app.route('/api/admin/send-monthly-report', methods=['POST'])
@auth_required
@roles_required('admin')
def trigger_monthly_report():
    # Manually trigger monthly reports

@app.route('/api/admin/export-all-data', methods=['POST'])
@auth_required
@roles_required('admin')
def trigger_admin_export():
    # Export all system data to admin email
```

#### Export Routes
```python
@app.route('/api/export', methods=['GET'])
@auth_required
def export_bookings():
    # Export user's bookings to CSV via email
```

---

### 4. `tasks.py` - Celery Background Tasks

**Purpose**: Asynchronous email and data export tasks

**Tasks**:

#### Task 1: Booking Confirmation Email
```python
@celery.task(bind=True, name='tasks.send_booking_confirmation')
def send_booking_confirmation(self, booking_id):
    # Triggered: After every booking
    # Sends: Instant confirmation email with booking details
```

#### Task 2: Daily User Reminders
```python
@celery.task(bind=True, name='tasks.send_daily_reminders')
def send_daily_reminders(self):
    # Triggered: Daily at 6:00 PM (Celery Beat)
    # Sends: Reminder to users inactive for 7+ days
```

#### Task 3: Monthly Reports
```python
@celery.task(bind=True, name='tasks.send_monthly_report')
def send_monthly_report(self):
    # Triggered: 1st of month at 12:00 AM (Celery Beat)
    # Sends: 
    #   - Comprehensive report to admin
    #   - Personal reports to all users
```

#### Task 4: Daily Admin Report
```python
@celery.task(bind=True, name='tasks.send_daily_admin_report')
def send_daily_admin_report(self):
    # Triggered: Daily at 8:00 AM (Celery Beat)
    # Sends: Previous day's statistics to admin
```

#### Task 5: User CSV Export
```python
@celery.task(bind=True, name='tasks.export_user_bookings')
def export_user_bookings(self, user_id):
    # Triggered: User clicks "Export CSV"
    # Sends: Email with CSV attachment
```

#### Task 6: Admin Export All Data
```python
@celery.task(bind=True, name='tasks.export_admin_all_data')
def export_admin_all_data(self):
    # Triggered: Admin clicks "Export All Data"
    # Sends: Email with 3 CSV files (users, lots, bookings)
```

**Email Configuration**:
```python
ADMIN_EMAIL = "nbhanuvardhanreddy@gmail.com"  # All admin emails go here
smtp_user = "nbhanuvardhanreddy@gmail.com"
smtp_password = 'irsi znit bdyl hwcu'  # Gmail App Password
```

---

### 5. `celery_config.py` - Celery Configuration

**Purpose**: Configure Celery and schedule periodic tasks

**Configuration**:
```python
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True
```

**Beat Schedule** (Cron Jobs):
```python
beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  # 6:00 PM daily
    },
    'monthly-reports': {
        'task': 'tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # 1st of month
    },
    'daily-admin-report': {
        'task': 'tasks.send_daily_admin_report',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    },
}
```

---

### 6. `celery_worker.py` - Celery Worker Initialization

**Purpose**: Initialize Celery worker with Flask app context

```python
from celery import Celery
from app import app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = make_celery(app)
```

---

### 7. `asynctask_demo.py` - Email Testing Script

**Purpose**: Test email system without manual triggers

**Usage**:
```bash
# Send all email types
python asynctask_demo.py --all

# Send specific email types
python asynctask_demo.py --reminders
python asynctask_demo.py --reports
python asynctask_demo.py --exports

# Test mode (doesn't actually send)
python asynctask_demo.py --all --test
```

**Features**:
- Sends emails to all users at once
- Tests all 6 email types
- Provides detailed console output
- Validates email configuration

---

## 🔐 Authentication & Authorization

### JWT Token Flow

1. **User Login**:
   ```python
   POST /auth/login
   Body: { "email": "user@example.com", "password": "pass123" }
   Response: { "token": "eyJhbGc...", "user": {...} }
   ```

2. **Token Storage**:
   - Frontend stores in localStorage
   - Sent in Authorization header: `Bearer <token>`

3. **Token Validation**:
   ```python
   from flask_security import auth_required
   
   @app.route('/api/protected')
   @auth_required
   def protected_route():
       return jsonify({"message": "Access granted"})
   ```

4. **Role Checking**:
   ```python
   from flask_security import roles_required
   
   @app.route('/api/admin-only')
   @auth_required
   @roles_required('admin')
   def admin_route():
       return jsonify({"message": "Admin access"})
   ```

---

## 📊 Business Logic

### Booking Cost Calculation

```python
def calculate_booking_cost(booking, lot):
    if booking.booking_type == 'instant':
        # For instant bookings
        if booking.end_time:
            duration = (booking.end_time - booking.start_time).total_seconds() / 3600
            return duration * lot.price_per_hour
    
    elif booking.booking_type == 'reserved':
        # For reserved bookings
        if booking.reserved_start and booking.reserved_end:
            duration = (booking.reserved_end - booking.reserved_start).total_seconds() / 3600
            return duration * lot.price_per_hour
    
    return 0.0
```

### Spot Allocation Algorithm

```python
def allocate_spot(lot_id):
    # Find first available spot in ascending order
    available_spot = ParkingSpot.query.filter_by(
        lot_id=lot_id,
        status='Available'
    ).order_by(ParkingSpot.spot_number).first()
    
    if available_spot:
        available_spot.status = 'Occupied'
        db.session.commit()
        return available_spot
    
    return None  # No available spots
```

### User Inactivity Detection

```python
def find_inactive_users(days=7):
    inactive_since = datetime.now() - timedelta(days=days)
    
    inactive_users = []
    for user in User.query.filter(User.roles.any(name='user')).all():
        last_booking = Booking.query.filter_by(user_id=user.id)\
            .order_by(Booking.start_time.desc()).first()
        
        if not last_booking or last_booking.start_time < inactive_since:
            inactive_users.append(user)
    
    return inactive_users
```

---

## 🗄️ Database Operations

### Create Tables

```python
from app import app, db

with app.app_context():
    db.create_all()
    print("Database tables created!")
```

### Reset Database

```python
from app import app, db

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset!")
```

### Seed Sample Data

```python
from app import app, db, user_datastore
from models import ParkingLot, ParkingSpot

with app.app_context():
    # Create admin
    admin = user_datastore.create_user(
        email="admin@parking.com",
        password=hash_password("admin123"),
        roles=['admin']
    )
    
    # Create test user
    user = user_datastore.create_user(
        email="test@example.com",
        username="testuser",
        password=hash_password("test123"),
        roles=['user']
    )
    
    # Create parking lot
    lot = ParkingLot(name="Downtown Parking", capacity=20, price_per_hour=5.0)
    db.session.add(lot)
    db.session.commit()
    
    # Create spots
    for i in range(1, lot.capacity + 1):
        spot = ParkingSpot(spot_number=i, lot_id=lot.id)
        db.session.add(spot)
    
    db.session.commit()
    print("Sample data seeded!")
```

---

## 📧 Email System

### SMTP Configuration

**Gmail Setup**:
1. Enable 2-Step Verification in Google Account
2. Generate App Password:
   - Google Account → Security → 2-Step Verification → App Passwords
   - Select "Mail" and "Other (Custom name)"
   - Copy 16-character password
3. Update `tasks.py`:
   ```python
   smtp_user = "your-email@gmail.com"
   smtp_password = 'xxxx xxxx xxxx xxxx'  # 16-char App Password
   ```

### Email Templates

All emails use HTML templates with:
- Responsive design
- Bootstrap-inspired styling
- Color-coded statistics
- Clear call-to-action buttons
- Plain text fallback

### Email Delivery

```python
import smtplib
from email.message import EmailMessage

def send_email(to_email, subject, body_text, body_html, attachments=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype='html')
    
    # Attach files
    if attachments:
        for filename, file_data in attachments:
            msg.add_attachment(file_data, maintype='text', 
                             subtype='csv', filename=filename)
    
    # Send
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
    server.quit()
```

---

## 🧪 Testing

### Test API Endpoints

```bash
# Register user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"test123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Get lots (with token)
curl -X GET http://localhost:5000/api/lots \
  -H "Authorization: Bearer YOUR_TOKEN"

# Book spot
curl -X POST http://localhost:5000/api/book \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lot_id":1,"booking_type":"instant"}'
```

### Test Email System

```bash
# Test all email types
python asynctask_demo.py --all

# Test specific types
python asynctask_demo.py --reminders --test
```

---

## 🚨 Error Handling

### Common HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET/POST |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 500 | Internal Error | Server error |

### Error Response Format

```json
{
  "error": "Error type",
  "message": "Human-readable description"
}
```

---

## 📦 Dependencies

```txt
Flask==2.3.0
Flask-SQLAlchemy==3.0.5
Flask-Security-Too==5.3.0
Flask-CORS==4.0.0
Celery==5.3.0
Redis==4.5.5
SQLAlchemy==2.0.19
Werkzeug==2.3.6
```

---

## 🔧 Configuration

### `config.py`

```python
class Config:
    SECRET_KEY = 'your-secret-key-change-in-production'
    SECURITY_PASSWORD_SALT = 'your-salt-change-in-production'
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/parking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    SECURITY_TOKEN_MAX_AGE = 86400  # 24 hours
    
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    CORS_ORIGINS = 'http://localhost:5173'
```

---

## 🚀 Deployment Considerations

### Production Checklist

- [ ] Change SECRET_KEY and SECURITY_PASSWORD_SALT
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set Flask debug=False
- [ ] Use production WSGI server (Gunicorn)
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS for HTTPS
- [ ] Use environment variables for secrets
- [ ] Set up Redis authentication
- [ ] Configure email rate limiting
- [ ] Add request logging
- [ ] Set up monitoring (Sentry, etc.)

### Environment Variables

```bash
export FLASK_ENV=production
export SECRET_KEY=<strong-random-key>
export DATABASE_URL=postgresql://user:pass@localhost/parking
export REDIS_URL=redis://localhost:6379/0
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
```

---

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Flask-Security Documentation](https://flask-security-too.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)

---

## 🔗 Related Documentation

- Main README: [../README.md](../README.md)
- Frontend README: [../frontend/README.md](../frontend/README.md)

---

**Last Updated**: November 27, 2025  
**Backend Version**: 1.0.0  
**Flask Version**: 2.3.0

