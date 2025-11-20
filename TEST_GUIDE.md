# Testing Guide - Vehicle Parking Management System

## Pre-Testing Checklist

- [ ] Redis is running (`redis-cli ping` returns PONG)
- [ ] Flask app is running (http://localhost:5000 accessible)
- [ ] Celery worker is running (optional but recommended)
- [ ] Database is created (instance/parking.db exists)

## Test Scenarios

### Milestone 1: Database Models ✅

**Test:**
1. Start Flask app
2. Check console for: "Admin user created: admin@parking.com / admin123"
3. Verify `instance/parking.db` exists
4. Check tables: User, Role, ParkingLot, ParkingSpot, Booking

**Expected Result:**
- Database file created
- Admin user seeded
- All tables present

---

### Milestone 2: Authentication ✅

**Test Admin Login:**
1. Go to http://localhost:5000
2. Enter email: `admin@parking.com`
3. Enter password: `admin123`
4. Click "Login"

**Expected Result:**
- Redirect to Admin Dashboard
- Shows "admin@parking.com (admin)" in navbar

**Test User Registration:**
1. Click "Need an account? Register"
2. Enter email: `test@example.com`
3. Enter username: `testuser`
4. Enter password: `test123`
5. Click "Register"

**Expected Result:**
- Success message displayed
- Redirect to User Dashboard
- Shows "test@example.com (user)" in navbar

**Test User Login:**
1. Logout
2. Login with: `test@example.com` / `test123`

**Expected Result:**
- Redirect to User Dashboard

---

### Milestone 3: Admin Dashboard ✅

**Test Create Parking Lot:**
1. Login as admin
2. Fill form:
   - Lot Name: "Downtown Parking"
   - Capacity: 10
   - Price per Hour: 5.00
3. Click "Create Lot"

**Expected Result:**
- Success message: "Parking lot created successfully!"
- New lot appears in "Parking Lots" section
- Shows: Available: 10, Occupied: 0

**Test View Spots:**
1. Click "View" button on created lot
2. Check spot grid

**Expected Result:**
- Shows 10 spots (#1 to #10)
- All spots are green (Available)

**Test View Users:**
1. Scroll to "Registered Users" section

**Expected Result:**
- Shows test@example.com with 0 total bookings

**Test Delete Lot:**
1. Create another lot: "Test Lot", 5 spots, $3/hour
2. Click "Delete" button
3. Confirm deletion

**Expected Result:**
- Success message: "Parking lot deleted successfully!"
- Lot removed from list

---

### Milestone 4: User Dashboard ✅

**Test Book Parking Spot:**
1. Login as user (test@example.com)
2. Select "Downtown Parking" from dropdown
3. Click "Book Now"

**Expected Result:**
- Success message: "Spot #1 booked successfully!"
- "Active Booking" card appears
- Shows lot name, spot number, start time
- "Release Spot" button visible

**Test Cannot Book Multiple Spots:**
1. Try to book another spot while one is active

**Expected Result:**
- Error: "You already have an active booking"

**Test Release Spot:**
1. Click "Release Spot" button in Active Booking card
2. Confirm

**Expected Result:**
- Success message: "Spot released! Total cost: $X.XX"
- Active booking card disappears
- Booking appears in history table with cost

**Test Booking History:**
1. Scroll to "Booking History" section

**Expected Result:**
- Shows completed booking with:
  - Lot name
  - Spot number
  - Start time
  - End time
  - Cost
  - Status: "Completed"

---

### Milestone 5: Cost Calculation ✅

**Test Cost Accuracy:**
1. Login as user
2. Book a spot
3. Note the start time
4. Wait 1 minute (or adjust system time for testing)
5. Release spot
6. Check cost

**Expected Formula:**
```
Duration (hours) = (End Time - Start Time) / 3600 seconds
Cost = Duration × Price per Hour
```

**Example:**
- Price: $5/hour
- Duration: 30 minutes = 0.5 hours
- Expected Cost: $2.50

---

### Milestone 6: Analytics & Charts ✅

**Test Admin Analytics:**
1. Login as admin
2. Check statistics cards at top
3. Scroll to "Revenue by Lot" chart

**Expected Result:**
- Total Lots: correct count
- Available/Occupied spots: correct
- Total Revenue: sum of completed bookings
- Bar chart showing revenue per lot

**Test User Analytics:**
1. Login as user (with some booking history)
2. Check statistics cards at top
3. Scroll to "Monthly Bookings" chart

**Expected Result:**
- Total Bookings: correct count
- Total Spent: correct sum
- Line chart showing bookings over 6 months

---

### Milestone 7: Redis Caching ✅

**Test Cache Working:**
1. Open terminal: `redis-cli`
2. Run: `KEYS *`
3. Login and view lots
4. Check Redis again: `GET all_lots`

**Expected Result:**
- Cache key `all_lots` present
- Contains JSON data
- TTL: 300 seconds (5 minutes)

**Test Cache Invalidation:**
1. Check cache: `redis-cli GET all_lots`
2. Create a new lot as admin
3. Check cache again

**Expected Result:**
- Cache deleted after lot creation
- New request rebuilds cache

**Manual Cache Test:**
```bash
# In terminal
redis-cli

# Check cache
KEYS *
GET all_lots

# Check TTL (time to live)
TTL all_lots

# Clear all cache (for testing)
FLUSHDB
```

---

### Milestone 8: Celery Jobs ✅

**Test CSV Export:**
1. Login as user with booking history
2. Click "Export CSV" button in Booking History section

**Expected Result:**
- Success message: "CSV export started! You will receive an email when ready."
- Email received with CSV attachment (if mail configured)
- CSV contains all bookings with correct data

**Manual Celery Test:**
```bash
# In backend directory
python
>>> from tasks import export_csv_task
>>> export_csv_task.delay(1)  # Replace 1 with actual user ID
```

**Test Daily Reminder (Manual Trigger):**
```bash
cd backend
python
>>> from tasks import send_daily_reminder
>>> send_daily_reminder()
```

**Expected Result:**
- Returns: "Daily reminders sent to X inactive users"
- Email sent to users with no bookings in 7+ days

**Test Monthly Report (Manual Trigger):**
```bash
cd backend
python
>>> from tasks import send_monthly_report
>>> send_monthly_report()
```

**Expected Result:**
- HTML email sent with monthly summary
- Includes: bookings, most used lot, total spent

**Check Celery Beat Schedule:**
```bash
cd backend
celery -A celery_worker.celery inspect scheduled
```

---

## Complete Test Flow

### Full User Journey
1. **Register** → test2@example.com
2. **Login** → Redirect to dashboard
3. **View Lots** → See available parking
4. **Book Spot** → Downtown Parking, Spot #2
5. **Active Booking** → See current parking details
6. **Wait 2 minutes** → Simulate parking duration
7. **Release Spot** → Calculate cost
8. **View History** → See completed booking
9. **Export CSV** → Download history
10. **Logout** → Return to login screen

### Full Admin Journey
1. **Login** → admin@parking.com
2. **View Dashboard** → See statistics
3. **Create Lot** → "Airport Parking", 20 spots, $10/hour
4. **View Spots** → See all 20 green spots
5. **View Users** → See registered users
6. **Check Analytics** → Revenue chart updates
7. **Try Delete** → Cannot delete if occupied
8. **Wait for user release** → Try delete again
9. **Successful Delete** → Lot removed

---

## Performance Testing

### Cache Performance
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test without cache (first request)
ab -n 100 -c 10 -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/lots

# Test with cache (subsequent requests)
ab -n 1000 -c 50 -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/lots
```

**Expected Result:**
- Cached requests should be significantly faster
- Higher requests per second

---

## Error Handling Tests

### Test Business Rules

**Cannot Delete Occupied Lot:**
1. Admin creates lot with 5 spots
2. User books a spot
3. Admin tries to delete lot
- Expected: Error "Cannot delete lot with occupied spots"

**Cannot Reduce Capacity Below Occupied:**
1. Admin creates lot with 10 spots
2. User books spot #1
3. Admin tries to reduce capacity to 0
- Expected: Error "Cannot reduce capacity while spots are occupied"

**No Double Booking:**
1. User books spot #1
2. User tries to book spot #2 without releasing
- Expected: Error "You already have an active booking"

**Invalid Credentials:**
1. Try login with wrong password
- Expected: Error "Invalid credentials"

**Token Expiration:**
1. Login
2. Wait 24 hours (or manually expire token)
3. Try to make API call
- Expected: Error "Token has expired"

---

## Success Criteria Checklist

- [ ] Admin can create 1 lot with 5 spots
- [ ] User can register and login
- [ ] User can book spot (auto-allocated)
- [ ] User can release spot
- [ ] Cost calculated correctly
- [ ] CSV export works
- [ ] Daily reminder sends email (check Celery logs)
- [ ] Redis caches `/api/lots` (verify with redis-cli)
- [ ] Bootstrap styling applied
- [ ] Charts display correctly
- [ ] All API endpoints return proper responses
- [ ] Error messages are user-friendly

---

## Debugging Tips

### Check Flask Logs
```bash
cd backend
python app.py
# Watch console for errors
```

### Check Celery Logs
```bash
cd backend
celery -A celery_worker.celery worker --loglevel=debug
```

### Check Redis
```bash
redis-cli
> PING
> KEYS *
> FLUSHDB  # Clear all cache
```

### Check Database
```bash
sqlite3 instance/parking.db
.tables
SELECT * FROM user;
SELECT * FROM parking_lot;
SELECT * FROM booking;
.quit
```

### Browser Console
- Open DevTools (F12)
- Check Console for JavaScript errors
- Check Network tab for API responses

---

## Video Demo Script

1. **Intro (30 sec)**
   - "This is the Vehicle Parking Management System"
   - "Built with Flask, Vue.js, Redis, and Celery"

2. **Approach (30 sec)**
   - "Followed 8 milestone structure"
   - "Implemented RBAC, caching, and async jobs"

3. **Features Demo (90 sec)**
   - Admin: Create lot, view spots, analytics
   - User: Book spot, release, view history
   - Show charts updating
   - Trigger CSV export

4. **Additional Features (30 sec)**
   - Redis caching demonstration
   - Celery jobs explanation
   - Responsive design showcase

Total: ~3 minutes (can expand to 5-10 min with detailed explanations)

