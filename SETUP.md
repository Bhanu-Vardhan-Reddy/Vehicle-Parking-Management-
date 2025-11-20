# Vehicle Parking App - Setup Guide

## Quick Start

### Prerequisites
1. Python 3.8 or higher
2. Redis Server
3. Git (for version control)

### Installation Steps

#### Option 1: Using Startup Scripts (Recommended)

**On Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**On Windows:**
```bash
run.bat
```

#### Option 2: Manual Setup

1. **Create Virtual Environment**
```bash
python -m venv venv
```

2. **Activate Virtual Environment**

On Linux/Mac:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Start Redis Server**

On Linux:
```bash
redis-server
```

On Mac (with Homebrew):
```bash
brew services start redis
```

On Windows:
Download Redis from: https://github.com/microsoftarchive/redis/releases
Or use Docker:
```bash
docker run -d -p 6379:6379 redis
```

5. **Start Flask Application**
```bash
cd backend
python app.py
```

The app will be available at: http://localhost:5000

6. **Start Celery Worker (Optional but Recommended)**

Open a new terminal:
```bash
cd backend
celery -A celery_worker.celery worker --loglevel=info
```

7. **Start Celery Beat Scheduler (Optional but Recommended)**

Open another terminal:
```bash
cd backend
celery -A celery_worker.celery beat --loglevel=info
```

Or combine worker and beat:
```bash
cd backend
celery -A celery_worker.celery worker --beat --loglevel=info
```

## Default Admin Credentials

- **Email:** admin@parking.com
- **Password:** admin123

## Testing the Application

### Admin Flow
1. Login with admin credentials
2. Create a parking lot (e.g., "Downtown Parking", 10 spots, $5/hour)
3. View the created spots (should show 10 available spots)
4. View registered users
5. Check analytics dashboard

### User Flow
1. Register a new user account
2. Login with user credentials
3. View available parking lots
4. Book a parking spot (will be auto-allocated)
5. Release the spot after some time
6. View booking history and cost
7. Export bookings as CSV

## Email Configuration (Optional)

To enable email notifications for reminders and reports, set these environment variables:

```bash
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USERNAME=your_email@gmail.com
export MAIL_PASSWORD=your_app_password
export MAIL_DEFAULT_SENDER=your_email@gmail.com
```

For Gmail, you need to create an App Password:
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"

## Project Structure

```
project_2/
├── backend/
│   ├── app.py              # Flask application
│   ├── models.py           # Database models
│   ├── routes.py           # API endpoints
│   ├── tasks.py            # Celery background jobs
│   ├── config.py           # Configuration
│   ├── celery_worker.py    # Celery worker entry point
│   └── requirements.txt    # Python dependencies
├── static/
│   └── app.js             # Vue.js frontend
├── templates/
│   └── index.html         # HTML template
├── instance/
│   └── parking.db         # SQLite database (auto-created)
├── run.sh                 # Linux/Mac startup script
├── run.bat                # Windows startup script
└── README.md              # Project documentation
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `GET /auth/verify` - Verify token

### Parking Lots
- `GET /api/lots` - List all lots (cached)
- `POST /api/lots` - Create lot (admin)
- `PUT /api/lots/<id>` - Update lot (admin)
- `DELETE /api/lots/<id>` - Delete lot (admin)

### Parking Spots
- `GET /api/spots/<lot_id>` - List spots (cached)

### Bookings
- `POST /api/book` - Book a spot
- `POST /api/release/<booking_id>` - Release spot
- `GET /api/bookings` - Get booking history

### Statistics
- `GET /api/stats/admin` - Admin statistics
- `GET /api/stats/user` - User statistics

### Export
- `GET /api/export` - Trigger CSV export job

## Background Jobs

### 1. Daily Reminder
- Runs every day at 6 PM
- Sends email to users inactive for 7+ days

### 2. Monthly Report
- Runs on 1st of each month at midnight
- Sends HTML email with monthly activity summary

### 3. CSV Export
- User-triggered
- Exports booking history as CSV
- Sends via email attachment

## Troubleshooting

### Redis Connection Error
- Make sure Redis is running: `redis-cli ping` (should return PONG)
- Check Redis port: default is 6379

### Database Issues
- Delete `instance/parking.db` to reset database
- Restart Flask app to recreate tables and admin user

### Port Already in Use
- Change port in `backend/app.py`: `app.run(port=5001)`
- Update `static/app.js`: `const API_BASE = 'http://localhost:5001';`

### Email Not Sending
- Check MAIL_* environment variables
- For testing without email, you can skip Celery worker

## Development Tips

### Reset Database
```bash
rm instance/parking.db
cd backend && python app.py
```

### View Redis Cache
```bash
redis-cli
> KEYS *
> GET all_lots
```

### Monitor Celery Tasks
```bash
celery -A celery_worker.celery events
```

## Production Deployment Notes

1. Change `SECRET_KEY` and `SECURITY_PASSWORD_SALT` in production
2. Use proper SMTP server for email
3. Use PostgreSQL/MySQL instead of SQLite for production
4. Set `debug=False` in Flask app
5. Use Gunicorn/uWSGI for Flask
6. Use Nginx for reverse proxy
7. Configure proper Redis persistence

## Git Commands

Initialize repository:
```bash
git init
git add .
git commit -m "Milestone-VP-MAD2 Final-Submission"
```

Add collaborator:
1. Push to GitHub
2. Go to Settings → Collaborators
3. Add: MADII-cs2006

## Support

For issues or questions, refer to:
- Flask Documentation: https://flask.palletsprojects.com/
- Vue.js Documentation: https://vuejs.org/
- Celery Documentation: https://docs.celeryproject.org/
- Redis Documentation: https://redis.io/documentation

