

import sys
import os
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery_worker import celery, app
from tasks import send_daily_reminder, send_monthly_report, export_user_bookings
from models import User, Booking


def print_banner():
    """Print demo banner"""
    print("\n" + "="*70)
    print(" 🚀 ASYNC TASK DEMO - Parking Management System")
    print("="*70)
    print(f" Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def print_section(title):
    """Print section header"""
    print("\n" + "-"*70)
    print(f" {title}")
    print("-"*70)


def get_all_users():
    """Get all non-admin users from database"""
    with app.app_context():
        users = User.query.filter(
            ~User.roles.any(name='admin')
        ).all()
        return users


def demo_daily_reminders():
    """Demo: Send daily reminder emails to all inactive users"""
    print_section("📧 DAILY REMINDER EMAILS")
    
    print("\n📋 Task: Send reminder to users who haven't booked in 7+ days")
    print("   Type: HTML Email with 'Book Now' button")
    print("   Trigger: Automated (6:00 PM daily)")
    
    print("\n🔄 Queuing task...")
    
    with app.app_context():
        result = send_daily_reminder.delay()
        print(f"   ✅ Task ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Wait for completion
        print("\n⏳ Waiting for task to complete...", end='', flush=True)
        start_time = time.time()
        
        while not result.ready() and time.time() - start_time < 30:
            time.sleep(0.5)
            print(".", end='', flush=True)
        
        print()
        
        if result.ready():
            task_result = result.get()
            print(f"\n✅ TASK COMPLETED!")
            print(f"   Users Notified: {task_result.get('users_notified', 0)}")
            print(f"   Emails Sent To: {', '.join(task_result.get('emails', [])) or 'None (all users active)'}")
            print(f"   Executed At: {task_result.get('executed_at', 'N/A')}")
            return True
        else:
            print(f"\n⚠️  Task still running after 30s")
            print(f"   Check Celery worker logs for progress")
            return False


def demo_monthly_reports():
    """Demo: Send monthly report emails to all active users"""
    print_section("📊 MONTHLY REPORT EMAILS")
    
    print("\n📋 Task: Send monthly parking summary to all users")
    print("   Type: HTML Email with statistics table")
    print("   Content: Bookings, spending, most used lot")
    print("   Trigger: Automated (1st of month, 12:00 AM)")
    
    print("\n🔄 Queuing task...")
    
    with app.app_context():
        result = send_monthly_report.delay()
        print(f"   ✅ Task ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Wait for completion
        print("\n⏳ Waiting for task to complete...", end='', flush=True)
        start_time = time.time()
        
        while not result.ready() and time.time() - start_time < 30:
            time.sleep(0.5)
            print(".", end='', flush=True)
        
        print()
        
        if result.ready():
            task_result = result.get()
            print(f"\n✅ TASK COMPLETED!")
            print(f"   Reports Sent: {task_result.get('reports_sent', 0)}")
            print(f"   Month: {task_result.get('month', 'N/A')}")
            print(f"   Emails Sent To: {', '.join(task_result.get('emails', [])) or 'None (no bookings last month)'}")
            print(f"   Executed At: {task_result.get('executed_at', 'N/A')}")
            return True
        else:
            print(f"\n⚠️  Task still running after 30s")
            print(f"   Check Celery worker logs for progress")
            return False


def demo_csv_exports():
    """Demo: Send CSV export emails to all users"""
    print_section("📄 CSV EXPORT EMAILS")
    
    print("\n📋 Task: Export booking history and email CSV to all users")
    print("   Type: HTML Email with CSV file attachment")
    print("   Content: Complete booking history in spreadsheet format")
    print("   Trigger: User-triggered (Export button)")
    
    users = get_all_users()
    
    if not users:
        print("\n⚠️  No users found in database!")
        return False
    
    print(f"\n👥 Found {len(users)} user(s) in database")
    
    print("\n🔄 Queuing tasks for all users...")
    
    task_results = []
    
    for user in users:
        print(f"\n   User: {user.email} (ID: {user.id})")
        
        with app.app_context():
            result = export_user_bookings.delay(user.id)
            print(f"   ✅ Task ID: {result.id}")
            task_results.append((user, result))
    
    print(f"\n✅ All {len(task_results)} export tasks queued!")
    
    # Wait for all tasks to complete
    print("\n⏳ Waiting for all tasks to complete...", end='', flush=True)
    start_time = time.time()
    
    completed = 0
    while completed < len(task_results) and time.time() - start_time < 60:
        completed = sum(1 for _, r in task_results if r.ready())
        time.sleep(0.5)
        print(".", end='', flush=True)
    
    print()
    
    # Display results
    print(f"\n✅ {completed}/{len(task_results)} TASKS COMPLETED!")
    
    for user, result in task_results:
        if result.ready():
            try:
                task_result = result.get()
                status = "✅" if task_result.get('email_sent', False) else "⚠️"
                print(f"\n   {status} {user.email}")
                print(f"      Bookings Exported: {task_result.get('total_bookings', 0)}")
                print(f"      Email Sent: {'Yes' if task_result.get('email_sent', False) else 'No (CSV saved locally)'}")
                print(f"      File: {task_result.get('filename', 'N/A')}")
            except Exception as e:
                print(f"\n   ❌ {user.email}")
                print(f"      Error: {str(e)}")
        else:
            print(f"\n   ⏳ {user.email}")
            print(f"      Still processing...")
    
    return completed == len(task_results)


def demo_all_tasks():
    """Demo: Send all types of emails to all users"""
    print_section("🎯 SENDING ALL EMAIL TYPES TO ALL USERS")
    
    print("\n📧 This will send:")
    print("   1. Daily reminder emails (to inactive users)")
    print("   2. Monthly report emails (to users with bookings)")
    print("   3. CSV export emails (to all users)")
    
    print("\n⚠️  WARNING: This will send actual emails!")
    confirm = input("\nContinue? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ Demo cancelled by user")
        return
    
    results = {
        'daily_reminders': False,
        'monthly_reports': False,
        'csv_exports': False
    }
    
    # Execute all tasks
    results['daily_reminders'] = demo_daily_reminders()
    time.sleep(2)  # Brief pause between task types
    
    results['monthly_reports'] = demo_monthly_reports()
    time.sleep(2)
    
    results['csv_exports'] = demo_csv_exports()
    
    # Print final summary
    print_section("📊 DEMO SUMMARY")
    
    for task_name, success in results.items():
        status = "✅ SUCCESS" if success else "⚠️  INCOMPLETE"
        print(f"   {task_name.replace('_', ' ').title()}: {status}")
    
    total_success = sum(results.values())
    print(f"\n   Total: {total_success}/{len(results)} tasks completed successfully")
    
    if total_success == len(results):
        print("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")
        print("   Check user email inboxes for notifications")
    else:
        print("\n⚠️  Some tasks did not complete")
        print("   Check Celery worker logs for details")


def test_mode():
    """Test mode - show what would be sent without actually sending"""
    print_section("🧪 TEST MODE - DRY RUN")
    
    print("\n📋 This will show what emails would be sent WITHOUT sending them")
    
    users = get_all_users()
    
    if not users:
        print("\n⚠️  No users found in database!")
        print("   Create users via registration endpoint first")
        return
    
    print(f"\n👥 Found {len(users)} user(s) in database:\n")
    
    for user in users:
        print(f"   User ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username or 'N/A'}")
        
        # Check last booking
        with app.app_context():
            last_booking = Booking.query.filter_by(user_id=user.id).order_by(
                Booking.start_time.desc()
            ).first()
            
            if last_booking:
                days_ago = (datetime.now() - last_booking.start_time).days
                print(f"   Last Booking: {days_ago} days ago")
            else:
                days_ago = None
                print(f"   Last Booking: Never")
            
            total_bookings = Booking.query.filter_by(user_id=user.id).count()
            print(f"   Total Bookings: {total_bookings}")
            
            # Determine which emails would be sent
            print(f"\n   Would Receive:")
            if not last_booking or days_ago >= 7:
                print(f"      ✅ Daily Reminder (inactive 7+ days)")
            else:
                print(f"      ❌ Daily Reminder (active user)")
            
            if total_bookings > 0:
                print(f"      ✅ Monthly Report (has bookings)")
            else:
                print(f"      ❌ Monthly Report (no bookings)")
            
            print(f"      ✅ CSV Export (all users)")
            print()


def show_usage():
    """Show usage instructions"""
    print("\n📖 USAGE:")
    print("   python asynctask_demo.py                # Send all email types")
    print("   python asynctask_demo.py --reminder     # Only send daily reminders")
    print("   python asynctask_demo.py --monthly      # Only send monthly reports")
    print("   python asynctask_demo.py --csv          # Only send CSV exports")
    print("   python asynctask_demo.py --test         # Test mode (dry run)")
    print("   python asynctask_demo.py --help         # Show this help")


def check_prerequisites():
    """Check if Redis and Celery are running"""
    print_section("🔍 CHECKING PREREQUISITES")
    
    all_ok = True
    
    # Check Redis
    print("\n1. Redis Connection...")
    try:
        result = celery.control.inspect().active()
        if result is not None:
            print("   ✅ Redis is running")
        else:
            print("   ❌ Redis not connected")
            all_ok = False
    except Exception as e:
        print(f"   ❌ Redis connection failed: {str(e)}")
        print("   Start Redis: redis-server")
        all_ok = False
    
    # Check Celery workers
    print("\n2. Celery Workers...")
    try:
        result = celery.control.inspect().active()
        if result and len(result) > 0:
            print(f"   ✅ {len(result)} worker(s) active")
            for worker_name in result.keys():
                print(f"      - {worker_name}")
        else:
            print("   ❌ No Celery workers detected")
            print("   Start worker: celery -A celery_worker.celery worker --loglevel=info --pool=solo")
            all_ok = False
    except Exception as e:
        print(f"   ❌ Celery check failed: {str(e)}")
        all_ok = False
    
    # Check Database
    print("\n3. Database Connection...")
    try:
        with app.app_context():
            user_count = User.query.count()
            print(f"   ✅ Database connected")
            print(f"   {user_count} user(s) in database")
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
        print("   Initialize database: python app.py")
        all_ok = False
    
    if not all_ok:
        print("\n❌ Prerequisites not met!")
        print("   Fix the issues above before running demo")
        return False
    
    print("\n✅ All prerequisites met!")
    return True


def main():
    """Main entry point"""
    print_banner()
    
    # Parse arguments
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        show_usage()
        return
    
    # Check prerequisites
    if not check_prerequisites():
        return
    
    # Run appropriate demo
    if '--test' in args:
        test_mode()
    elif '--reminder' in args:
        demo_daily_reminders()
    elif '--monthly' in args:
        demo_monthly_reports()
    elif '--csv' in args:
        demo_csv_exports()
    else:
        demo_all_tasks()
    
    # Print footer
    print("\n" + "="*70)
    print(f" End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

