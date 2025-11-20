# Vehicle Parking Management System

A multi-user web application for managing parking lots, parking spots, and vehicle reservations.

## Project Overview

This is a Modern Application Development II (MAD-II) project that implements a comprehensive vehicle parking management system with role-based access control.

## Features

### Admin Features
- Create, edit, and delete parking lots
- Auto-generate parking spots based on lot capacity
- View all parking spots and their status (Available/Occupied)
- View all registered users
- View analytics and revenue reports

### User Features
- Register and login
- View available parking lots
- Book parking spots (auto-allocated by system)
- Release parking spots with automatic cost calculation
- View booking history and personal analytics
- Export booking data as CSV

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Vue.js (via CDN)
- **Database:** SQLite with SQLAlchemy ORM
- **Caching:** Redis
- **Task Queue:** Celery + Redis
- **UI Framework:** Bootstrap 5
- **Charts:** Chart.js

## Setup Instructions

### Prerequisites
- Python 3.8+
- Redis Server

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd project_2
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

4. Start Redis server
```bash
redis-server
```

5. Initialize database
```bash
cd backend
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

6. Run Flask application
```bash
flask run
```

7. Start Celery worker (in separate terminal)
```bash
celery -A backend.tasks worker --loglevel=info
```

8. Start Celery beat (in separate terminal)
```bash
celery -A backend.tasks beat --loglevel=info
```

## Default Admin Credentials
- Email: admin@parking.com
- Password: admin123

## Project Structure

```
project_2/
├── backend/
│   ├── app.py           # Flask application entry point
│   ├── models.py        # Database models
│   ├── routes.py        # API endpoints
│   ├── tasks.py         # Celery background jobs
│   ├── config.py        # Configuration settings
│   └── requirements.txt # Python dependencies
├── static/
│   └── app.js          # Vue.js application
├── templates/
│   └── index.html      # Main HTML template
└── instance/
    └── parking.db      # SQLite database
```

## API Endpoints

### Authentication
- POST `/auth/register` - User registration
- POST `/auth/login` - User/Admin login

### Parking Lots
- GET `/api/lots` - List all parking lots
- POST `/api/lots` - Create new lot (Admin only)
- PUT `/api/lots/<id>` - Update lot (Admin only)
- DELETE `/api/lots/<id>` - Delete lot (Admin only)

### Parking Spots
- GET `/api/spots/<lot_id>` - List spots in a lot

### Bookings
- POST `/api/book` - Book a parking spot
- POST `/api/release/<booking_id>` - Release a spot
- GET `/api/bookings` - Get user's booking history

### Analytics
- GET `/api/stats/admin` - Admin statistics
- GET `/api/stats/user` - User statistics

### Export
- GET `/api/export` - Trigger CSV export job

## Background Jobs

1. **Daily Reminder** - Sends email reminders to inactive users (runs at 6 PM daily)
2. **Monthly Report** - Generates and emails monthly activity reports (runs on 1st of each month)
3. **CSV Export** - User-triggered async job to export booking data

## License

This project is developed for educational purposes as part of MAD-II coursework.

## Collaborator

GitHub Username: MADII-cs2006
