# 🚀 Quick Start Guide - Vehicle Parking App

## ⚡ Get Running in 5 Minutes

### Step 1: Install Dependencies (1 min)
```bash
pip install -r backend/requirements.txt
```

### Step 2: Start Redis (1 min)
```bash
# Linux/Mac
redis-server

# Windows with Docker
docker run -d -p 6379:6379 redis

# Or download Windows Redis from:
# https://github.com/microsoftarchive/redis/releases
```

### Step 3: Start Flask App (1 min)
```bash
cd backend
python app.py
```

You'll see:
```
Admin user created: admin@parking.com / admin123
* Running on http://127.0.0.1:5000
```

### Step 4: Access the App (1 min)
Open browser: **http://localhost:5000**

Login as Admin:
- Email: `admin@parking.com`
- Password: `admin123`

### Step 5: Test Basic Flow (1 min)

**As Admin:**
1. Create a parking lot: "Downtown", 5 spots, $5/hour
2. Click "View" to see 5 green spots

**As User:**
1. Click "Need an account? Register"
2. Register: `user@test.com` / `user123`
3. Book a spot in Downtown lot
4. Release the spot → See cost calculated!

---

## 🎯 What You Just Built

✅ **Backend:** Flask REST API with 15 endpoints  
✅ **Frontend:** Vue.js 3 with Bootstrap 5  
✅ **Database:** SQLite with 5 tables  
✅ **Auth:** JWT token-based authentication  
✅ **Cache:** Redis caching for performance  
✅ **Jobs:** Celery background tasks  
✅ **Charts:** Analytics with Chart.js  

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/app.py` | Flask app + DB initialization |
| `backend/models.py` | Database models (User, Lot, Spot, Booking) |
| `backend/routes.py` | API endpoints (auth, lots, bookings) |
| `backend/tasks.py` | Celery jobs (reminders, reports, CSV) |
| `static/app.js` | Vue.js frontend logic |
| `templates/index.html` | Main HTML template |

---

## 🔧 Optional: Start Background Jobs

### Terminal 2: Celery Worker
```bash
cd backend
celery -A celery_worker.celery worker --loglevel=info
```

### Terminal 3: Celery Beat (Scheduler)
```bash
cd backend
celery -A celery_worker.celery beat --loglevel=info
```

---

## 📊 Core Features

### Admin Can:
- ✅ Create/Edit/Delete parking lots
- ✅ View all spots with status (green/red)
- ✅ See all registered users
- ✅ View revenue analytics

### User Can:
- ✅ Register and login
- ✅ Book parking (auto-allocated)
- ✅ Release parking (cost calculated)
- ✅ View booking history
- ✅ Export bookings as CSV

### System Features:
- ✅ Redis caching (lots & spots)
- ✅ Daily email reminders
- ✅ Monthly activity reports
- ✅ CSV export via email
- ✅ Real-time charts

---

## 🧪 Quick Test

### Test Redis Cache:
```bash
redis-cli
> KEYS *
> GET all_lots
> TTL all_lots
> exit
```

### Test Database:
```bash
sqlite3 instance/parking.db
.tables
SELECT * FROM parking_lot;
.quit
```

### Test API:
```bash
# Get lots (requires token from login)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/lots
```

---

## 📚 Full Documentation

- **SETUP.md** - Detailed installation guide
- **TEST_GUIDE.md** - Complete testing scenarios
- **PROJECT_SUMMARY.md** - Full implementation details
- **README.md** - Project overview

---

## 🎓 For Submission

### 1. Video Demo (5-10 min)
- Show admin creating lot
- Show user booking/releasing
- Explain caching and background jobs
- Show charts updating

### 2. Project Report (3-5 pages)
- Student details
- ER diagram (see db.mdc)
- API endpoints (15 total)
- Tech stack used
- AI usage declaration
- Video link

### 3. Git Commits
```bash
git init
git add .
git commit -m "Milestone-VP-MAD2 Final-Submission"
```

### 4. Add Collaborator
- Push to GitHub
- Settings → Collaborators
- Add: **MADII-cs2006**

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Redis connection error | Start Redis: `redis-server` |
| Port 5000 in use | Kill process or change port in app.py |
| Database not found | Delete `instance/parking.db` and restart |
| Import errors | Run `pip install -r backend/requirements.txt` |
| Admin not found | Check console for admin creation message |

---

## 💡 Pro Tips

1. **Reset Everything:**
   ```bash
   rm -rf instance/
   redis-cli FLUSHDB
   cd backend && python app.py
   ```

2. **Watch Logs:**
   - Flask: Check terminal where app.py runs
   - Redis: `redis-cli MONITOR`
   - Celery: Worker terminal shows task execution

3. **Email Testing:**
   - Set MAIL_* env variables
   - Use Gmail app password
   - Test with: `tasks.send_daily_reminder()`

4. **Performance:**
   - First API call: slow (cache miss)
   - Next calls: fast (cache hit)
   - Check with browser DevTools Network tab

---

## 🎉 Success Checklist

- [ ] Flask app running on port 5000
- [ ] Redis running and connectable
- [ ] Admin login works
- [ ] User registration works
- [ ] Can create parking lot
- [ ] Can book parking spot
- [ ] Can release with cost calculation
- [ ] Charts display correctly
- [ ] Cache working (verify with redis-cli)

---

## 📞 Next Steps

1. ✅ Test all features (use TEST_GUIDE.md)
2. ✅ Record video demonstration
3. ✅ Write project report
4. ✅ Commit code to GitHub
5. ✅ Add collaborator
6. ✅ Submit ZIP + report

---

**You're all set! 🚀**

Access: http://localhost:5000  
Admin: admin@parking.com / admin123

**Happy Parking! 🚗**

