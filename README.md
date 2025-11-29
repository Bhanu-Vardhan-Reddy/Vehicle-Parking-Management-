# 🚗 Vehicle Parking Management System

A full-stack parking management application with real-time booking, automated email notifications, and comprehensive reporting.

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Application Flow](#application-flow)
- [Email System](#email-system)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Testing](#testing)

---

## 🎯 Overview

A modern parking management system that allows:
- **Admins** to manage parking lots, view all bookings, and access system-wide analytics
- **Users** to book parking spots, view booking history, and receive automated notifications
- **Automated Tasks** for daily reminders, monthly reports, booking confirmations, and data exports

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework for RESTful API
- **SQLAlchemy** - ORM for database operations
- **Flask-Security** - Authentication & role-based access control (RBAC)
- **SQLite** - Lightweight database
- **Redis** - Message broker for Celery
- **Celery** - Distributed task queue for background jobs
- **Celery Beat** - Scheduler for periodic tasks

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Bootstrap 5** - CSS framework for responsive UI
- **Axios** - HTTP client for API calls

### Email System
- **SMTP (Gmail)** - Email delivery
- **HTML Templates** - Beautiful email notifications

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Vue.js)                       │
│                  http://localhost:5173                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    Login     │  │    Admin     │  │     User     │    │
│  │  Component   │  │  Dashboard   │  │  Dashboard   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ HTTP/REST API (JWT Auth)
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  BACKEND (Flask API)                        │
│                 http://localhost:5000                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Flask Routes (routes.py)                │  │
│  │  /auth/*, /api/lots, /api/book, /api/release, ...  │  │
│  └────────────┬──────────────────────┬──────────────────┘  │
│               │                      │                      │
│  ┌────────────▼────────┐  ┌─────────▼──────────┐          │
│  │  SQLAlchemy ORM    │  │   Celery Tasks     │          │
│  │   (models.py)      │  │    (tasks.py)      │          │
│  └────────────┬────────┘  └─────────┬──────────┘          │
└───────────────┼───────────────────────┼─────────────────────┘
                │                       │
     ┌──────────▼──────────┐  ┌────────▼──────────┐
     │   SQLite Database   │  │  Redis (Broker)   │
     │   parking.db        │  │  localhost:6379   │
     └─────────────────────┘  └────────┬──────────┘
                                       │
                          ┌────────────▼────────────┐
                          │   Celery Worker         │
                          │   (Background Tasks)    │
                          │   + Celery Beat         │
                          │   (Cron Scheduler)      │
                          └────────┬────────────────┘
                                   │
                          ┌────────▼────────────┐
                          │   SMTP Server       │
                          │   (Gmail)           │
                          └─────────────────────┘
```

---

## ✨ Features

### 👨‍💼 Admin Features
- ✅ Create, edit, and delete parking lots
- ✅ View all parking spots with real-time status (Available/Occupied)
- ✅ View all registered users
- ✅ Access system-wide statistics and charts
- ✅ Trigger manual email notifications (daily reminders, monthly reports)
- ✅ Export all system data to email (users, lots, bookings)
- ✅ Receive daily reports with previous day's statistics
- ✅ Receive monthly comprehensive analytics reports

### 👤 User Features
- ✅ Register and login
- ✅ Book parking spots (auto-allocated, instant or reserved)
- ✅ Release/vacate parking spots
- ✅ View booking history with costs
- ✅ Export booking history to CSV
- ✅ Receive booking confirmation emails
- ✅ Receive monthly reports with personal analytics

### 🤖 Automated Tasks (Celery)
- ✅ **Booking Confirmation** - Instant email after each booking
- ✅ **Daily Admin Report** - 8:00 AM daily with previous day's stats
- ✅ **Daily User Reminder** - 6:00 PM to inactive users (7+ days)
- ✅ **Monthly Reports** - 1st of each month at midnight (admin + users)
- ✅ **CSV Export** - User-triggered with email notification

---

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **Redis Server**
- **Gmail Account** (for SMTP)

### 1. Clone Repository

```bash
git clone <repository-url>
cd "project 2"
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

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
```

Backend will run at: **http://localhost:5000**

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run at: **http://localhost:5173**

### 4. Redis Setup

**Windows:**
```bash
# Download Redis from: https://github.com/microsoftarchive/redis/releases
# Or use Docker:
docker run -d -p 6379:6379 redis
```

**Linux/Mac:**
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server
```

### 5. Celery Worker Setup

**Terminal 1 - Celery Worker:**
```bash
cd backend
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

**Terminal 2 - Celery Beat (Scheduler):**
```bash
cd backend
celery -A celery_worker.celery beat --loglevel=info
```

### 6. Email Configuration

Update `backend/tasks.py` with your Gmail credentials:

```python
# Line 15-16
smtp_user = "your-email@gmail.com"
smtp_password = 'your-app-password'  # Gmail App Password

# Line 29 (Admin email)
ADMIN_EMAIL = "admin-email@gmail.com"
```

**Enable Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password for "Mail"
4. Use that password in `smtp_password`

---

## 🔄 Application Flow

### User Registration & Login Flow

```
1. User visits http://localhost:5173
2. Clicks "Register" → Enters email, username, password
3. Frontend sends POST /auth/register to backend
4. Backend creates user with 'user' role
5. User logs in → Backend returns JWT token
6. Frontend stores token in localStorage
7. User redirected to User Dashboard
```

### Admin Login Flow

```
1. Admin logs in with credentials (nbhanuvardhanreddy@gmail.com / admin123)
2. Backend validates and returns JWT token with 'admin' role
3. Frontend stores token and redirects to Admin Dashboard
```

### Booking Flow (Instant Booking)

```
1. User clicks "Book Now" on a parking lot
2. Frontend sends POST /api/book with { lot_id, booking_type: 'instant' }
3. Backend:
   a. Finds first available spot in lot
   b. Updates spot status to 'Occupied'
   c. Creates booking record with start_time
   d. Triggers Celery task: send_booking_confirmation
4. Backend responds with booking details
5. Frontend updates UI
6. Celery worker sends confirmation email to user
```

### Release Flow

```
1. User clicks "Release" on active booking
2. Frontend sends POST /api/release/<booking_id>
3. Backend:
   a. Sets booking.end_time = NOW()
   b. Calculates cost: (end_time - start_time) * price_per_hour
   c. Updates booking.total_cost
   d. Updates spot status to 'Available'
4. Backend responds with final cost
5. Frontend displays cost and updates UI
```

### Reserved Booking Flow

```
1. User selects "Reserve for Later" and picks date/time range
2. Frontend sends POST /api/book with:
   { lot_id, booking_type: 'reserved', reserved_start, reserved_end }
3. Backend:
   a. Validates reservation time (must be future)
   b. Finds available spot
   c. Creates booking with 'Reserved' status
   d. Triggers confirmation email
4. User receives email with reservation details
```

### Admin Lot Management Flow

```
CREATE LOT:
1. Admin enters name, capacity, price_per_hour
2. Backend creates lot and auto-generates N parking spots
3. All spots initialized with status='Available'

EDIT LOT:
1. Admin updates capacity (e.g., 10 → 15)
2. Backend adds 5 new spots OR removes last 5 if capacity decreased

DELETE LOT:
1. Admin clicks delete
2. Backend checks if any spot is 'Occupied'
3. If yes → Error: "Cannot delete lot with occupied spots"
4. If no → Delete lot (cascade deletes all spots)
```

---

## 📧 Email System

### Email Types

| Email Type | Trigger | Recipients | Frequency |
|------------|---------|------------|-----------|
| **Booking Confirmation** | After each booking | User who booked | Instant |
| **Daily User Reminder** | Celery Beat Cron | Inactive users (7+ days) | Daily 6:00 PM |
| **Daily Admin Report** | Celery Beat Cron | Admin | Daily 8:00 AM |
| **Monthly User Report** | Celery Beat Cron | All users | 1st of month, 12:00 AM |
| **Monthly Admin Report** | Celery Beat Cron | Admin | 1st of month, 12:00 AM |
| **CSV Export** | User clicks "Export CSV" | Requesting user | On-demand |
| **Admin Export All** | Admin clicks "Export All Data" | Admin | On-demand |

### Email Templates

All emails use **HTML templates** with:
- Professional Bootstrap-inspired styling
- Responsive design
- Summary statistics with color-coded metrics
- CSV attachments where applicable
- Clear call-to-action buttons

### Cron Schedule (Celery Beat)

```python
# backend/celery_config.py

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

## 📡 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login user/admin | No |

**Request Body (Register):**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "roles": ["user"]
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Parking Lot Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/lots` | List all lots | Yes | All |
| POST | `/api/lots` | Create lot | Yes | Admin |
| PUT | `/api/lots/<id>` | Update lot | Yes | Admin |
| DELETE | `/api/lots/<id>` | Delete lot | Yes | Admin |

**Create Lot Request:**
```json
{
  "name": "Downtown Parking",
  "capacity": 50,
  "price_per_hour": 5.0
}
```

### Booking Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/api/book` | Book a spot | Yes | User |
| POST | `/api/release/<booking_id>` | Release spot | Yes | User |
| GET | `/api/bookings` | Get user's bookings | Yes | User |
| GET | `/api/spots/<lot_id>` | Get spots in lot | Yes | All |

**Book Spot Request (Instant):**
```json
{
  "lot_id": 1,
  "booking_type": "instant"
}
```

**Book Spot Request (Reserved):**
```json
{
  "lot_id": 1,
  "booking_type": "reserved",
  "reserved_start": "2025-12-01T10:00:00",
  "reserved_end": "2025-12-01T18:00:00"
}
```

### Admin Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/users` | List all users | Yes | Admin |
| POST | `/api/admin/send-daily-reminder` | Trigger daily reminders | Yes | Admin |
| POST | `/api/admin/send-monthly-report` | Trigger monthly reports | Yes | Admin |
| POST | `/api/admin/export-all-data` | Export all data to email | Yes | Admin |

### Export Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/export` | Export user's bookings to CSV | Yes | User |

---

## 🗄️ Database Schema

### Tables

#### User
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255) NOT NULL,
    fs_uniquifier VARCHAR(255) UNIQUE NOT NULL
);
```

#### Role
```sql
CREATE TABLE role (
    id INTEGER PRIMARY KEY,
    name VARCHAR(80) UNIQUE,
    description VARCHAR(255)
);
```

#### ParkingLot
```sql
CREATE TABLE parking_lot (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL,
    price_per_hour FLOAT NOT NULL
);
```

#### ParkingSpot
```sql
CREATE TABLE parking_spot (
    id INTEGER PRIMARY KEY,
    spot_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Available',
    lot_id INTEGER,
    FOREIGN KEY (lot_id) REFERENCES parking_lot(id)
);
```

#### Booking
```sql
CREATE TABLE booking (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    spot_id INTEGER,
    booking_type VARCHAR(20) DEFAULT 'instant',
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    reserved_start DATETIME,
    reserved_end DATETIME,
    total_cost FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (spot_id) REFERENCES parking_spot(id)
);
```

### Relationships

```
User ──< Booking >── ParkingSpot >── ParkingLot
  │
  └──< roles_users >── Role
```

- **One-to-Many**: User → Bookings
- **One-to-Many**: ParkingSpot → Bookings
- **One-to-Many**: ParkingLot → ParkingSpots
- **Many-to-Many**: User ↔ Role (via roles_users)

---

## 📁 Project Structure

```
project_2/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── models.py               # SQLAlchemy models
│   ├── routes.py               # API endpoints
│   ├── config.py               # Configuration
│   ├── tasks.py                # Celery tasks (email jobs)
│   ├── celery_config.py        # Celery configuration
│   ├── celery_worker.py        # Celery worker initialization
│   ├── asynctask_demo.py       # Email testing script
│   ├── requirements.txt        # Python dependencies
│   └── instance/
│       └── parking.db          # SQLite database
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.vue           # Login/Register page
│   │   │   ├── AdminDashboard.vue  # Admin interface
│   │   │   └── UserDashboard.vue   # User interface
│   │   ├── App.vue                 # Root component
│   │   └── main.js                 # Entry point with router
│   ├── public/
│   │   └── index.html              # HTML entry point
│   ├── package.json                # Node dependencies
│   └── vite.config.js              # Vite configuration
│
├── exports/                    # Generated CSV exports
│   ├── user_<id>/              # User-specific exports
│   └── admin/                  # Admin system exports
│
├── venv/                       # Python virtual environment
└── README.md                   # This file
```

---

## 🧪 Testing

### Manual Testing

#### Test User Registration & Login
```bash
# Register a new user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"test123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

#### Test Email System

Run the comprehensive email demo:

```bash
cd backend
python asynctask_demo.py --all
```

Options:
- `--reminders` - Send daily reminders only
- `--reports` - Send monthly reports only
- `--exports` - Send CSV exports only
- `--all` - Send all email types
- `--test` - Use test mode (doesn't actually send emails)

### Default Admin Credentials

```
Email: nbhanuvardhanreddy@gmail.com
Password: admin123
```

---

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/parking.db'
SECRET_KEY = 'your-secret-key-here'
SECURITY_PASSWORD_SALT = 'your-salt-here'
CORS_ORIGINS = 'http://localhost:5173'
```

### Redis Configuration

```python
# Broker URL
broker_url = 'redis://localhost:6379/0'

# Result backend
result_backend = 'redis://localhost:6379/0'
```

---

## 📊 Business Logic

### Cost Calculation

```python
# For instant bookings (released)
duration_hours = (end_time - start_time).total_seconds() / 3600
total_cost = duration_hours * lot.price_per_hour

# For reserved bookings (completed)
duration_hours = (reserved_end - reserved_start).total_seconds() / 3600
total_cost = duration_hours * lot.price_per_hour
```

### Spot Allocation

```python
# Auto-allocate first available spot
available_spot = ParkingSpot.query.filter_by(
    lot_id=lot_id,
    status='Available'
).order_by(ParkingSpot.spot_number).first()
```

### User Activity Check (for reminders)

```python
# Find inactive users (no booking in 7+ days)
inactive_since = datetime.now() - timedelta(days=7)
last_booking = Booking.query.filter_by(user_id=user.id)\
    .order_by(Booking.start_time.desc()).first()

if not last_booking or last_booking.start_time < inactive_since:
    send_reminder_email(user)
```

---

## 🚨 Troubleshooting

### Common Issues

**1. Redis Connection Error**
```
Error: [WinError 10061] No connection could be made
Solution: Ensure Redis server is running on localhost:6379
```

**2. Celery Worker Not Starting**
```
Error: Celery worker fails to start
Solution: Use --pool=solo on Windows
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

**3. Email Not Sending**
```
Error: SMTPAuthenticationError
Solution: 
- Enable 2-Step Verification in Google Account
- Generate App Password
- Use App Password in tasks.py, not regular password
```

**4. CORS Error**
```
Error: Access-Control-Allow-Origin
Solution: Check CORS_ORIGINS in config.py matches frontend URL
```

**5. Database Locked**
```
Error: database is locked
Solution: Close all connections and restart Flask server
```

---

## 📈 Performance Considerations

- **Redis Caching**: Lot data cached for 5 minutes
- **Database Indexing**: Indexes on foreign keys and status columns
- **Async Tasks**: All emails sent via Celery (non-blocking)
- **Connection Pooling**: SQLAlchemy connection pool for database
- **Lazy Loading**: Vue components loaded on-demand

---

## 🔐 Security Features

- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Role-Based Access Control** - Admin vs User permissions
- ✅ **Password Hashing** - Bcrypt for secure password storage
- ✅ **CORS Protection** - Restricted to frontend origin
- ✅ **SQL Injection Prevention** - SQLAlchemy ORM parameterization
- ✅ **Input Validation** - Server-side validation for all inputs

---

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review the [API Documentation](#api-documentation)
- Test email system with `asynctask_demo.py`

---

## 📄 License

This project is for educational purposes as part of a vehicle parking management system demonstration.

---


