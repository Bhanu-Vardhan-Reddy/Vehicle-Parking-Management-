"""
Celery Tasks for Background Jobs
Milestone 8: Daily Reminder, Monthly Report, CSV Export, Booking Confirmations, Admin Reports
"""
from celery_worker import celery
from datetime import datetime, timedelta
from models import db, User, Booking, ParkingSpot, ParkingLot
from email_notif import email_alert
from sqlalchemy import func
import csv
import os
from io import StringIO

# ==========================================
# Task 1: Daily Reminder (Scheduled)
# ==========================================

@celery.task(bind=True, name='tasks.send_daily_reminder')
def send_daily_reminder(self):
    """
    Send reminder to users who haven't booked in 7+ days
    Scheduled: Daily at 6 PM
    """
    try:
        self.update_state(state='PROGRESS', meta={'message': 'Starting daily reminder task'})
        
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        # Get all users (excluding admin)
        users = User.query.filter(
            ~User.roles.any(name='admin')
        ).all()
        
        inactive_users = []
        
        for user in users:
            # Get user's last booking
            last_booking = Booking.query.filter_by(user_id=user.id).order_by(
                Booking.start_time.desc()
            ).first()
            
            # If no booking or last booking was 7+ days ago
            if not last_booking or last_booking.start_time < seven_days_ago:
                inactive_users.append(user.email)
                
                # Send actual email reminder
                subject = "🚗 We miss you! Come park with us"
                body = f"""Hi {user.username or user.email},

We noticed you haven't booked a parking spot in over 7 days!

Great news - we have plenty of spots available. 
Book your spot today and enjoy hassle-free parking!

Visit: http://localhost:5173

Best regards,
Parking Management Team"""
                
                html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                        <h2 style="color: #0d6efd;">🚗 We Miss You!</h2>
                        <p>Hi <strong>{user.username or user.email}</strong>,</p>
                        <p>We noticed you haven't booked a parking spot in over <strong>7 days</strong>!</p>
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #198754; margin: 20px 0;">
                            <p style="margin: 0;"><strong>Great news</strong> - we have plenty of spots available!</p>
                        </div>
                        <p>Book your spot today and enjoy hassle-free parking!</p>
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:5173" style="background-color: #0d6efd; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Book Now</a>
                        </p>
                        <p style="color: #6c757d; font-size: 14px;">Best regards,<br>Parking Management Team</p>
                    </div>
                </body>
                </html>
                """
                
                try:
                    email_alert(subject, body, user.email, html)
                    print(f"✅ Email sent to {user.email}")
                    
                    # Log for tracking
                    os.makedirs('logs', exist_ok=True)
                    with open('logs/daily_reminders.txt', 'a') as f:
                        f.write(f"{datetime.now()}: Email sent to {user.email}\n")
                except Exception as e:
                    print(f"❌ Failed to send email to {user.email}: {str(e)}")
        
        return {
            'status': 'success',
            'task': 'daily_reminder',
            'executed_at': datetime.now().isoformat(),
            'users_notified': len(inactive_users),
            'emails': inactive_users
        }
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'error', 'message': str(e)}


# ==========================================
# Task 2: Monthly Report (Scheduled)
# ==========================================

@celery.task(bind=True, name='tasks.send_monthly_report')
def send_monthly_report(self):
    """
    Send monthly report to all users and admin with comprehensive analytics
    Scheduled: 1st day of month at midnight
    """
    try:
        self.update_state(state='PROGRESS', meta={'message': 'Starting monthly report generation'})
        
        # Get last month's date range
        today = datetime.now()
        first_day_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if today.month == 1:
            last_month_start = first_day_this_month.replace(year=today.year - 1, month=12)
        else:
            last_month_start = first_day_this_month.replace(month=today.month - 1)
        
        last_month_end = first_day_this_month
        
        # Get all users (excluding admin)
        users = User.query.filter(
            ~User.roles.any(name='admin')
        ).all()
        
        reports_sent = []
        
        for user in users:
            # Get user's bookings for last month
            bookings = Booking.query.filter(
                Booking.user_id == user.id,
                Booking.start_time >= last_month_start,
                Booking.start_time < last_month_end
            ).all()
            
            if not bookings:
                continue  # Skip users with no activity
            
            total_bookings = len(bookings)
            total_spent = sum(b.total_cost for b in bookings if b.status == 'Completed')
            
            # Find most used lot
            lot_usage = {}
            for booking in bookings:
                spot = ParkingSpot.query.get(booking.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                lot_usage[lot.name] = lot_usage.get(lot.name, 0) + 1
            
            most_used_lot = max(lot_usage, key=lot_usage.get) if lot_usage else 'N/A'
            
            # Generate plain text body
            body = f"""Hi {user.username or user.email},

Here's your parking activity for {last_month_start.strftime('%B %Y')}:

📈 Statistics:
- Total Bookings: {total_bookings}
- Total Spent: ${total_spent:.2f}
- Most Used Lot: {most_used_lot}

Thank you for choosing our parking service!

Best regards,
Parking Management Team"""
            
            # Generate HTML report with booking details
            booking_rows = ""
            for booking in bookings:
                spot = ParkingSpot.query.get(booking.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                booking_rows += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{lot.name}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">#{spot.spot_number}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${booking.total_cost:.2f}</td>
                </tr>
                """
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #0d6efd;">📊 Monthly Parking Summary</h2>
                    <p>Hi <strong>{user.username or user.email}</strong>,</p>
                    <p>Here's your parking activity for <strong>{last_month_start.strftime('%B %Y')}</strong>:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #198754;">📈 Statistics</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 5px 0;">📋 <strong>Total Bookings:</strong> {total_bookings}</li>
                            <li style="padding: 5px 0;">💰 <strong>Total Spent:</strong> ${total_spent:.2f}</li>
                            <li style="padding: 5px 0;">🅿️ <strong>Most Used Lot:</strong> {most_used_lot}</li>
                        </ul>
                    </div>
                    
                    <h3 style="color: #0d6efd;">📋 Booking Details</h3>
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <thead>
                            <tr style="background-color: #0d6efd; color: white;">
                                <th style="padding: 10px; text-align: left;">Parking Lot</th>
                                <th style="padding: 10px; text-align: center;">Spot</th>
                                <th style="padding: 10px; text-align: right;">Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            {booking_rows}
                        </tbody>
                    </table>
                    
                    <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                        Thank you for choosing our parking service!<br>
                        <strong>Parking Management Team</strong>
                    </p>
                </div>
            </body>
            </html>
            """
            
            subject = f"📊 Your Monthly Parking Summary - {last_month_start.strftime('%B %Y')}"
            
            try:
                email_alert(subject, body, user.email, html)
                print(f"✅ Monthly report sent to {user.email}")
                reports_sent.append(user.email)
                
                # Log for tracking
                os.makedirs('logs/monthly_reports', exist_ok=True)
                with open(f"logs/monthly_reports/{user.id}_{last_month_start.strftime('%Y_%m')}.txt", 'w') as f:
                    f.write(f"Report sent to {user.email} at {datetime.now()}\n")
            except Exception as e:
                print(f"❌ Failed to send monthly report to {user.email}: {str(e)}")
        
        # Send comprehensive monthly report to admin
        try:
            admin = User.query.join(User.roles).filter(db.func.lower(User.roles.any(name='admin'))).first()
            if admin:
                # Calculate system-wide statistics
                all_bookings = Booking.query.filter(
                    Booking.start_time >= last_month_start,
                    Booking.start_time < last_month_end
                ).all()
                
                total_system_bookings = len(all_bookings)
                total_revenue = sum(b.total_cost for b in all_bookings if b.status == 'Completed')
                total_users_active = len(reports_sent)
                
                # Most popular lot
                lot_usage = {}
                for booking in all_bookings:
                    spot = ParkingSpot.query.get(booking.spot_id)
                    lot = ParkingLot.query.get(spot.lot_id)
                    lot_usage[lot.name] = lot_usage.get(lot.name, 0) + 1
                
                most_popular_lot = max(lot_usage, key=lot_usage.get) if lot_usage else 'N/A'
                
                admin_subject = f"📊 Monthly System Report - {last_month_start.strftime('%B %Y')}"
                admin_body = f"""Monthly Parking System Report - Admin Summary

Month: {last_month_start.strftime('%B %Y')}

SYSTEM STATISTICS:
- Total Bookings: {total_system_bookings}
- Total Revenue: ${total_revenue:.2f}
- Active Users: {total_users_active}
- Reports Sent: {len(reports_sent)}
- Most Popular Lot: {most_popular_lot}

Parking Management System"""
                
                # Build lot performance table
                lot_rows = ""
                for lot_name, count in sorted(lot_usage.items(), key=lambda x: x[1], reverse=True):
                    lot_rows += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{lot_name}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{count}</td>
                    </tr>
                    """
                
                admin_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                        <h2 style="color: #0d6efd;">📊 Monthly System Report - Admin</h2>
                        <p style="font-size: 18px; color: #6c757d;">Month: <strong>{last_month_start.strftime('%B %Y')}</strong></p>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #198754;">💰 System Statistics</h3>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                                <div style="background-color: white; padding: 15px; border-left: 4px solid #0d6efd; border-radius: 3px;">
                                    <p style="margin: 0; color: #6c757d; font-size: 14px;">Total Bookings</p>
                                    <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #0d6efd;">{total_system_bookings}</p>
                                </div>
                                <div style="background-color: white; padding: 15px; border-left: 4px solid #198754; border-radius: 3px;">
                                    <p style="margin: 0; color: #6c757d; font-size: 14px;">Total Revenue</p>
                                    <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #198754;">${total_revenue:.2f}</p>
                                </div>
                                <div style="background-color: white; padding: 15px; border-left: 4px solid #ffc107; border-radius: 3px;">
                                    <p style="margin: 0; color: #6c757d; font-size: 14px;">Active Users</p>
                                    <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #ffc107;">{total_users_active}</p>
                                </div>
                                <div style="background-color: white; padding: 15px; border-left: 4px solid #dc3545; border-radius: 3px;">
                                    <p style="margin: 0; color: #6c757d; font-size: 14px;">Reports Sent</p>
                                    <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #dc3545;">{len(reports_sent)}</p>
                                </div>
                            </div>
                        </div>
                        
                        <h3 style="color: #0d6efd;">🏆 Lot Performance</h3>
                        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                            <thead>
                                <tr style="background-color: #0d6efd; color: white;">
                                    <th style="padding: 10px; text-align: left;">Parking Lot</th>
                                    <th style="padding: 10px; text-align: center;">Bookings</th>
                                </tr>
                            </thead>
                            <tbody>
                                {lot_rows}
                            </tbody>
                        </table>
                        
                        <div style="background-color: #d1ecf1; border-left: 4px solid #0dcaf0; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0;"><strong>🏅 Most Popular Lot:</strong> {most_popular_lot}</p>
                        </div>
                        
                        <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                            This is an automated monthly system report<br>
                            <strong>Parking Management System</strong>
                        </p>
                    </div>
                </body>
                </html>
                """
                
                email_alert(admin_subject, admin_body, admin.email, admin_html)
                print(f"✅ Monthly admin report sent to {admin.email}")
                reports_sent.append(f"{admin.email} (admin)")
        except Exception as e:
            print(f"❌ Failed to send monthly admin report: {str(e)}")
        
        return {
            'status': 'success',
            'task': 'monthly_report',
            'executed_at': datetime.now().isoformat(),
            'month': last_month_start.strftime('%B %Y'),
            'reports_sent': len(reports_sent),
            'emails': reports_sent
        }
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'error', 'message': str(e)}


# ==========================================
# Task 3: CSV Export (User-triggered)
# ==========================================

@celery.task(bind=True, name='tasks.export_user_bookings')
def export_user_bookings(self, user_id):
    """
    Generate CSV export of user's bookings
    Triggered: User clicks "Export My Bookings"
    """
    try:
        user_id = int(user_id)
        self.update_state(state='PROGRESS', meta={'message': f'Starting CSV generation for user {user_id}'})
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}
        
        # Get all user bookings
        bookings = Booking.query.filter_by(user_id=user_id).order_by(
            Booking.start_time.desc()
        ).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Booking ID',
            'Parking Lot',
            'Spot Number',
            'Type',
            'Start Time',
            'End Time',
            'Duration (hours)',
            'Cost ($)',
            'Status'
        ])
        
        # Write data
        for booking in bookings:
            spot = ParkingSpot.query.get(booking.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            
            # Calculate duration
            if booking.end_time:
                duration = (booking.end_time - booking.start_time).total_seconds() / 3600
            elif booking.reserved_start and booking.reserved_end:
                duration = (booking.reserved_end - booking.reserved_start).total_seconds() / 3600
            else:
                duration = 'Ongoing'
            
            writer.writerow([
                booking.id,
                lot.name,
                spot.spot_number,
                booking.booking_type.capitalize(),
                booking.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                booking.end_time.strftime('%Y-%m-%d %H:%M:%S') if booking.end_time else 'N/A',
                f"{duration:.2f}" if isinstance(duration, float) else duration,
                f"{booking.total_cost:.2f}",
                booking.status
            ])
        
            # Save CSV to file temporarily AND prepare for email
        os.makedirs('exports', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"exports/bookings_{user.id}_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            f.write(output.getvalue())
        
        # Prepare email with CSV attachment
        subject = "📄 Your Booking History CSV is Ready!"
        
        body = f"""Hi {user.username or user.email},

Your booking history has been exported successfully!

Total Bookings: {len(bookings)}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The CSV file is attached to this email.

Best regards,
Parking Management Team"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #0d6efd;">📄 Your Booking History CSV is Ready!</h2>
                <p>Hi <strong>{user.username or user.email}</strong>,</p>
                <p>Your booking history has been exported successfully!</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <ul style="list-style: none; padding: 0;">
                        <li style="padding: 5px 0;">📊 <strong>Total Bookings:</strong> {len(bookings)}</li>
                        <li style="padding: 5px 0;">🕐 <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        <li style="padding: 5px 0;">📎 <strong>Format:</strong> CSV (Comma-Separated Values)</li>
                    </ul>
                </div>
                
                <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #0c5460;">
                        <strong>📎 Attachment:</strong> The CSV file is attached to this email. You can open it with Excel, Google Sheets, or any spreadsheet application.
                    </p>
                </div>
                
                <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                    Best regards,<br>
                    <strong>Parking Management Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            # Send email with CSV attachment
            from email.message import EmailMessage
            import smtplib
            
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['To'] = user.email
            msg['From'] = "nbhanuvardhanreddy@gmail.com"
            
            # Add HTML content
            msg.set_content(body)  # Fallback plain text
            msg.add_alternative(html, subtype='html')  # HTML version
            
            # Attach CSV file
            with open(filename, 'rb') as f:
                csv_data = f.read()
                msg.add_attachment(csv_data, maintype='text', subtype='csv', filename=f'booking_history_{timestamp}.csv')
            
            # Send email
            smtp_user = "nbhanuvardhanreddy@gmail.com"
            smtp_password = 'irsi znit bdyl hwcu'
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ CSV export emailed to {user.email}")
            
            return {
                'status': 'success',
                'task': 'csv_export',
                'user_id': user_id,
                'user_email': user.email,
                'filename': filename,
                'total_bookings': len(bookings),
                'generated_at': datetime.now().isoformat(),
                'email_sent': True
            }
        except Exception as email_error:
            print(f"❌ Failed to email CSV to {user.email}: {str(email_error)}")
            # Still return success since CSV was generated
            return {
                'status': 'success',
                'task': 'csv_export',
                'user_id': user_id,
                'user_email': user.email,
                'filename': filename,
                'total_bookings': len(bookings),
                'generated_at': datetime.now().isoformat(),
                'email_sent': False,
                'email_error': str(email_error)
            }
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'error', 'user_id': user_id, 'message': str(e)}


# ==========================================
# Task 4: Booking Confirmation Email
# ==========================================

@celery.task(bind=True, name='tasks.send_booking_confirmation')
def send_booking_confirmation(self, booking_id):
    """
    Send booking confirmation email to user
    Triggered: Immediately after booking
    """
    try:
        self.update_state(state='PROGRESS', meta={'message': f'Sending booking confirmation for booking {booking_id}'})
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return {'status': 'error', 'message': 'Booking not found'}
        
        user = User.query.get(booking.user_id)
        spot = ParkingSpot.query.get(booking.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        
        # Prepare email content based on booking type
        if booking.booking_type == 'reserved':
            subject = f"✅ Reservation Confirmed - {lot.name} Spot #{spot.spot_number}"
            
            duration_hours = (booking.reserved_end - booking.reserved_start).total_seconds() / 3600
            
            body = f"""Hi {user.username or user.email},

Your parking reservation has been confirmed!

📋 Reservation Details:
- Parking Lot: {lot.name}
- Spot Number: #{spot.spot_number}
- Start Time: {booking.reserved_start.strftime('%Y-%m-%d %H:%M')}
- End Time: {booking.reserved_end.strftime('%Y-%m-%d %H:%M')}
- Duration: {duration_hours:.1f} hours
- Total Cost: ${booking.total_cost:.2f}
- Price Rate: ${lot.price_per_hour}/hour

⚠️ Important: Please arrive on time for your reservation.

Thank you for choosing our parking service!

Best regards,
Parking Management Team"""
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #198754;">✅ Reservation Confirmed!</h2>
                    <p>Hi <strong>{user.username or user.email}</strong>,</p>
                    <p>Your parking reservation has been confirmed!</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0d6efd;">📋 Reservation Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Parking Lot:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{lot.name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Spot Number:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">#{spot.spot_number}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Start Time:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{booking.reserved_start.strftime('%Y-%m-%d %H:%M')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>End Time:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{booking.reserved_end.strftime('%Y-%m-%d %H:%M')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Duration:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{duration_hours:.1f} hours</td>
                            </tr>
                            <tr style="background-color: #e7f3ff;">
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Total Cost:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #0d6efd; font-size: 18px;"><strong>${booking.total_cost:.2f}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px;"><strong>Price Rate:</strong></td>
                                <td style="padding: 8px;">${lot.price_per_hour}/hour</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>⚠️ Important:</strong> Please arrive on time for your reservation.</p>
                    </div>
                    
                    <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                        Thank you for choosing our parking service!<br>
                        <strong>Parking Management Team</strong>
                    </p>
                </div>
            </body>
            </html>
            """
        else:
            # Immediate booking
            subject = f"✅ Parking Confirmed - {lot.name} Spot #{spot.spot_number}"
            
            body = f"""Hi {user.username or user.email},

Your parking spot has been confirmed!

📋 Booking Details:
- Parking Lot: {lot.name}
- Spot Number: #{spot.spot_number}
- Start Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')}
- Price Rate: ${lot.price_per_hour}/hour

💡 Tip: Don't forget to release your spot when you leave to avoid extra charges.

Thank you for choosing our parking service!

Best regards,
Parking Management Team"""
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #198754;">✅ Parking Confirmed!</h2>
                    <p>Hi <strong>{user.username or user.email}</strong>,</p>
                    <p>Your parking spot has been confirmed!</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0d6efd;">📋 Booking Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Parking Lot:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{lot.name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Spot Number:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">#{spot.spot_number}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Start Time:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{booking.start_time.strftime('%Y-%m-%d %H:%M')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px;"><strong>Price Rate:</strong></td>
                                <td style="padding: 8px;">${lot.price_per_hour}/hour</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #d1ecf1; border-left: 4px solid #0dcaf0; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>💡 Tip:</strong> Don't forget to release your spot when you leave to avoid extra charges.</p>
                    </div>
                    
                    <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                        Thank you for choosing our parking service!<br>
                        <strong>Parking Management Team</strong>
                    </p>
                </div>
            </body>
            </html>
            """
        
        # Send email
        try:
            email_alert(subject, body, user.email, html)
            print(f"✅ Booking confirmation sent to {user.email}")
            
            return {
                'status': 'success',
                'task': 'booking_confirmation',
                'booking_id': booking_id,
                'user_email': user.email,
                'executed_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Failed to send confirmation to {user.email}: {str(e)}")
            return {
                'status': 'error',
                'task': 'booking_confirmation',
                'booking_id': booking_id,
                'error': str(e)
            }
            
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'error', 'message': str(e)}


# ==========================================
# Task 5: Daily Admin Report (Scheduled)
# ==========================================

@celery.task(bind=True, name='tasks.send_daily_admin_report')
def send_daily_admin_report(self):
    """
    Send daily report to admin with previous day's statistics
    Scheduled: Daily at 8:00 AM
    """
    try:
        self.update_state(state='PROGRESS', meta={'message': 'Generating daily admin report'})
        
        # Get admin user
        admin = User.query.join(User.roles).filter(db.func.lower(User.roles.any(name='admin'))).first()
        if not admin:
            return {'status': 'error', 'message': 'Admin user not found'}
        
        # Get yesterday's date range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        # Get yesterday's statistics
        bookings_yesterday = Booking.query.filter(
            Booking.start_time >= yesterday,
            Booking.start_time < today
        ).all()
        
        total_bookings = len(bookings_yesterday)
        immediate_bookings = sum(1 for b in bookings_yesterday if b.booking_type == 'immediate')
        reserved_bookings = sum(1 for b in bookings_yesterday if b.booking_type == 'reserved')
        
        # Revenue from completed bookings
        completed_yesterday = Booking.query.filter(
            Booking.end_time >= yesterday,
            Booking.end_time < today,
            Booking.status == 'Completed'
        ).all()
        
        revenue_yesterday = sum(b.total_cost for b in completed_yesterday)
        
        # New user registrations
        new_users = User.query.filter(
            ~User.roles.any(name='admin')
        ).count()
        
        # Current occupancy
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status='Occupied').count()
        occupancy_rate = (occupied_spots / total_spots * 100) if total_spots > 0 else 0
        
        # Most popular lot
        lot_bookings = {}
        for booking in bookings_yesterday:
            spot = ParkingSpot.query.get(booking.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            lot_bookings[lot.name] = lot_bookings.get(lot.name, 0) + 1
        
        most_popular_lot = max(lot_bookings, key=lot_bookings.get) if lot_bookings else 'N/A'
        most_popular_count = lot_bookings.get(most_popular_lot, 0) if lot_bookings else 0
        
        # Generate email
        subject = f"📊 Daily Admin Report - {yesterday.strftime('%B %d, %Y')}"
        
        body = f"""Daily Parking System Report

Date: {yesterday.strftime('%B %d, %Y')}

📈 YESTERDAY'S ACTIVITY:
- Total Bookings: {total_bookings}
  • Immediate: {immediate_bookings}
  • Reserved: {reserved_bookings}
- Revenue Generated: ${revenue_yesterday:.2f}
- New Users: {new_users}

🅿️ CURRENT STATUS:
- Occupancy Rate: {occupancy_rate:.1f}%
- Occupied Spots: {occupied_spots}/{total_spots}

🏆 TOP PERFORMER:
- Most Popular Lot: {most_popular_lot} ({most_popular_count} bookings)

Parking Management System
"""
        
        # Build booking details table
        booking_rows = ""
        for booking in bookings_yesterday[:10]:  # Show last 10 bookings
            spot = ParkingSpot.query.get(booking.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            user = User.query.get(booking.user_id)
            booking_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{booking.start_time.strftime('%H:%M')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{user.email}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{lot.name}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">#{spot.spot_number}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                    <span style="padding: 4px 8px; border-radius: 3px; font-size: 12px; background-color: {'#0dcaf0' if booking.booking_type == 'immediate' else '#6c757d'}; color: white;">
                        {booking.booking_type.capitalize()}
                    </span>
                </td>
            </tr>
            """
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #0d6efd;">📊 Daily Admin Report</h2>
                <p style="color: #6c757d; font-size: 16px;">Date: <strong>{yesterday.strftime('%B %d, %Y')}</strong></p>
                
                <div style="margin: 30px 0;">
                    <h3 style="color: #198754;">📈 Yesterday's Activity</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #0d6efd; border-radius: 3px;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">Total Bookings</p>
                            <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #0d6efd;">{total_bookings}</p>
                            <p style="margin: 5px 0 0 0; font-size: 12px; color: #6c757d;">
                                Immediate: {immediate_bookings} | Reserved: {reserved_bookings}
                            </p>
                        </div>
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #198754; border-radius: 3px;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">Revenue Generated</p>
                            <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #198754;">${revenue_yesterday:.2f}</p>
                            <p style="margin: 5px 0 0 0; font-size: 12px; color: #6c757d;">From {len(completed_yesterday)} completed bookings</p>
                        </div>
                    </div>
                </div>
                
                <div style="margin: 30px 0;">
                    <h3 style="color: #0dcaf0;">🅿️ Current Status</h3>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 3px;">
                        <p style="margin: 0; font-size: 14px;">
                            <strong>Occupancy Rate:</strong> 
                            <span style="font-size: 18px; color: {'#dc3545' if occupancy_rate > 80 else '#198754'};">{occupancy_rate:.1f}%</span>
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">
                            <strong>Occupied Spots:</strong> {occupied_spots}/{total_spots}
                        </p>
                    </div>
                </div>
                
                <div style="margin: 30px 0;">
                    <h3 style="color: #ffc107;">🏆 Top Performer</h3>
                    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 3px;">
                        <p style="margin: 0; font-size: 16px;">
                            <strong>Most Popular Lot:</strong> {most_popular_lot}
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 14px; color: #856404;">
                            {most_popular_count} bookings yesterday
                        </p>
                    </div>
                </div>
                
                <div style="margin: 30px 0;">
                    <h3>📋 Recent Bookings (Last 10)</h3>
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                        <thead>
                            <tr style="background-color: #0d6efd; color: white;">
                                <th style="padding: 10px; text-align: left;">Time</th>
                                <th style="padding: 10px; text-align: left;">User</th>
                                <th style="padding: 10px; text-align: left;">Lot</th>
                                <th style="padding: 10px; text-align: center;">Spot</th>
                                <th style="padding: 10px; text-align: left;">Type</th>
                            </tr>
                        </thead>
                        <tbody>
                            {booking_rows if booking_rows else '<tr><td colspan="5" style="padding: 20px; text-align: center; color: #6c757d;">No bookings yesterday</td></tr>'}
                        </tbody>
                    </table>
                </div>
                
                <p style="color: #6c757d; font-size: 14px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                    This is an automated daily report<br>
                    <strong>Parking Management System</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        # Send email to admin
        try:
            email_alert(subject, body, admin.email, html)
            print(f"✅ Daily admin report sent to {admin.email}")
            
            return {
                'status': 'success',
                'task': 'daily_admin_report',
                'date': yesterday.strftime('%Y-%m-%d'),
                'total_bookings': total_bookings,
                'revenue': float(revenue_yesterday),
                'admin_email': admin.email,
                'executed_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Failed to send admin report: {str(e)}")
            return {
                'status': 'error',
                'task': 'daily_admin_report',
                'error': str(e)
            }
            
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'error', 'message': str(e)}

