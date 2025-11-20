# 🔖 Git Commit Guide - Vehicle Parking App

## 📋 All Milestone Commits

This file contains all the git commit messages for each milestone as specified in the project requirements.

---

## Commit Sequence

### Milestone 0: GitHub Repository Setup
```bash
git init
git add README.md .gitignore
git commit -m "Milestone-0 VP-MAD2"
```

### Milestone 1: Database Models and Schema
```bash
git add backend/models.py backend/app.py backend/config.py backend/requirements.txt
git commit -m "Milestone-VP-MAD2 DB-Relationship"
```

### Milestone 2: Authentication & RBAC
```bash
git add backend/routes.py
git commit -m "Milestone-VP-MAD2 Auth-RBAC-Token"
```

### Milestone 3: Admin Dashboard
```bash
git add templates/index.html static/app.js
git commit -m "Milestone-VP-MAD2 Admin-Dashboard-Management"
```

### Milestone 4: User Dashboard
```bash
git add static/app.js templates/index.html
git commit -m "Milestone-VP-MAD2 User-Dashboard-Management"
```

### Milestone 5: Cost Calculation
```bash
git add backend/routes.py backend/models.py
git commit -m "Milestone-VP-MAD2 Reservation-Cost-Calculation"
```

### Milestone 6: Analytics & Charts
```bash
git add static/app.js templates/index.html backend/routes.py
git commit -m "Milestone-VP-MAD2 Charts-Analytics"
```

### Milestone 7: Redis Caching
```bash
git add backend/routes.py backend/app.py backend/config.py
git commit -m "Milestone-VP-MAD2 Redis-Caching"
```

### Milestone 8: Celery Jobs
```bash
git add backend/tasks.py backend/celery_worker.py backend/app.py
git commit -m "Milestone-VP-MAD2 Celery-Jobs"
```

### Final Submission
```bash
git add .
git commit -m "Milestone-VP-MAD2 Final-Submission"
git push origin main
```

---

## 🚀 Quick Commit All Milestones

If you want to commit everything at once (all milestones completed):

```bash
# Initialize repository
git init

# Add all files
git add .

# Commit with final submission message
git commit -m "Milestone-VP-MAD2 Final-Submission"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/vehicle-parking-mad2.git

# Push to GitHub
git push -u origin main
```

---

## 📝 Detailed Commit Log (What to Include)

### Milestone 0 Files:
- README.md
- .gitignore

### Milestone 1 Files:
- backend/models.py (User, Role, ParkingLot, ParkingSpot, Booking)
- backend/app.py (Flask initialization, admin seeding)
- backend/config.py (Configuration settings)
- backend/requirements.txt (Dependencies)

### Milestone 2 Files:
- backend/routes.py (Authentication endpoints: /auth/register, /auth/login, /auth/verify)
- JWT token generation and verification functions
- @token_required and @admin_required decorators

### Milestone 3 Files:
- backend/routes.py (Admin endpoints: lots CRUD, spots view, users list)
- templates/index.html (Admin dashboard UI)
- static/app.js (Admin Vue components and methods)

### Milestone 4 Files:
- backend/routes.py (User endpoints: book, release, bookings)
- templates/index.html (User dashboard UI)
- static/app.js (User Vue components and methods)

### Milestone 5 Files:
- backend/routes.py (Cost calculation in release endpoint)
- backend/models.py (calculate_cost method in Booking model)

### Milestone 6 Files:
- backend/routes.py (Stats endpoints: /api/stats/admin, /api/stats/user)
- templates/index.html (Chart.js CDN and canvas elements)
- static/app.js (Chart rendering methods)

### Milestone 7 Files:
- backend/routes.py (Cache decorators and invalidation)
- backend/app.py (Cache initialization)
- backend/config.py (Redis cache configuration)

### Milestone 8 Files:
- backend/tasks.py (All Celery tasks)
- backend/celery_worker.py (Celery entry point)
- backend/app.py (Celery initialization)

### Final Submission Files:
- All above files
- run.sh, run.bat (Startup scripts)
- SETUP.md, TEST_GUIDE.md (Documentation)
- QUICKSTART.md, PROJECT_SUMMARY.md
- ARCHITECTURE_OVERVIEW.md
- .cursor/rules/plan.mdc

---

## 🔍 Verify Commits

After committing, verify your commits:

```bash
# View commit history
git log --oneline

# Expected output (most recent first):
# abc1234 Milestone-VP-MAD2 Final-Submission
# def5678 Milestone-VP-MAD2 Celery-Jobs
# ghi9012 Milestone-VP-MAD2 Redis-Caching
# jkl3456 Milestone-VP-MAD2 Charts-Analytics
# mno7890 Milestone-VP-MAD2 Reservation-Cost-Calculation
# pqr1234 Milestone-VP-MAD2 User-Dashboard-Management
# stu5678 Milestone-VP-MAD2 Admin-Dashboard-Management
# vwx9012 Milestone-VP-MAD2 Auth-RBAC-Token
# yza3456 Milestone-VP-MAD2 DB-Relationship
# bcd7890 Milestone-0 VP-MAD2
```

---

## 📤 Push to GitHub

### First Time Push:
```bash
# Create repository on GitHub first (private)
# Then:

git remote add origin https://github.com/YOUR_USERNAME/vehicle-parking-mad2.git
git branch -M main
git push -u origin main
```

### Subsequent Pushes:
```bash
git push origin main
```

---

## 👥 Add Collaborator

After pushing to GitHub:

1. Go to your repository on GitHub
2. Click **Settings** (top right)
3. Click **Collaborators** (left sidebar)
4. Click **Add people**
5. Search for: **MADII-cs2006**
6. Click **Add MADII-cs2006 to this repository**
7. Confirm addition

**Important:** This must be done manually on GitHub. It cannot be done via command line.

---

## 📋 .gitignore Contents

Make sure these are in your `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
venv/
*.egg-info/

# Database
*.db
*.sqlite
*.sqlite3

# Redis
dump.rdb

# Celery
celerybeat-schedule
celerybeat.pid

# IDE
.vscode/
.idea/
.DS_Store

# Environment
.env
.flaskenv

# Instance
instance/

# Logs
*.log
```

---

## 🔄 If You Need to Reset

### Reset to specific commit:
```bash
git reset --hard COMMIT_HASH
```

### Reset all commits (start fresh):
```bash
rm -rf .git
git init
git add .
git commit -m "Milestone-VP-MAD2 Final-Submission"
```

### Undo last commit (keep changes):
```bash
git reset --soft HEAD~1
```

### Undo last commit (discard changes):
```bash
git reset --hard HEAD~1
```

---

## 📊 Commit Statistics

After all commits, you can view stats:

```bash
# Total commits
git rev-list --count HEAD

# Lines added/removed
git log --shortstat

# Files changed
git log --stat

# Contributors
git shortlog -sn
```

---

## ✅ Pre-Push Checklist

Before pushing:

- [ ] All files committed
- [ ] Commit messages follow milestone format
- [ ] .gitignore excludes unnecessary files
- [ ] No sensitive data (passwords, API keys) in code
- [ ] instance/ directory not committed
- [ ] venv/ directory not committed
- [ ] __pycache__/ not committed
- [ ] All documentation files included
- [ ] README.md is complete

---

## 🎓 For Submission

### Git Requirements:
1. ✅ All milestone commits with proper messages
2. ✅ Final submission commit
3. ✅ Pushed to private GitHub repository
4. ✅ Collaborator MADII-cs2006 added

### Submission Package:
```bash
# Create ZIP (exclude git, venv, cache)
zip -r vehicle-parking-mad2.zip . \
  -x "*.git*" \
  -x "*venv/*" \
  -x "*__pycache__*" \
  -x "*.pyc" \
  -x "*instance/*" \
  -x "*.db"
```

Or on Windows:
- Right-click project folder
- Send to → Compressed (zipped) folder
- Manually delete: .git, venv, __pycache__, instance folders from ZIP

---

## 📁 What Should Be in Git

### ✅ Include:
- All .py files (backend/)
- All .js files (static/)
- All .html files (templates/)
- All .md files (documentation)
- All .mdc files (.cursor/rules/)
- requirements.txt
- .gitignore
- run.sh, run.bat

### ❌ Exclude:
- instance/ (database)
- venv/ (virtual environment)
- __pycache__/ (Python cache)
- *.pyc (compiled Python)
- .env (environment variables)
- *.db, *.sqlite (database files)
- dump.rdb (Redis dump)
- celerybeat-schedule (Celery schedule)

---

## 🎯 Success Criteria

Your git repository should show:

```bash
$ git log --oneline
abc1234 Milestone-VP-MAD2 Final-Submission
def5678 Milestone-VP-MAD2 Celery-Jobs
ghi9012 Milestone-VP-MAD2 Redis-Caching
...
bcd7890 Milestone-0 VP-MAD2

$ git remote -v
origin  https://github.com/YOUR_USERNAME/vehicle-parking-mad2.git (fetch)
origin  https://github.com/YOUR_USERNAME/vehicle-parking-mad2.git (push)

$ git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

## 📞 Help

If you encounter issues:

```bash
# Check git status
git status

# Check remote
git remote -v

# Check last commit
git log -1

# Check branches
git branch

# Force push (use carefully)
git push -f origin main
```

---

**All commits should be pushed before final submission!** ✅

Make sure the GitHub repository is **private** and **MADII-cs2006** is added as a collaborator.

