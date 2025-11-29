from celery_worker import celery
from datetime import datetime, timedelta
from models import db, User, Booking, ParkingSpot, ParkingLot
from email_notif import email_alert
from sqlalchemy import func
import csv
import os
from io import StringIO

ADMIN_EMAIL = "nbhanuvardhanreddy@gmail.com"

@celery.task(bind=True, name='tasks.send_daily_reminder')
def send_daily_reminder(self):
    try:
        print("Starting daily reminder task")
        
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        users = User.query.filter(~User.roles.any(name='admin')).all()
        
        inactive_users = []
        
        for user in users:
            last_booking = Booking.query.filter_by(user_id=user.id).order_by(Booking.start_time.desc()).first()
            
            if not last_booking or last_booking.start_time < seven_days_ago:
                inactive_users.append(user.email)
                
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
                    os.makedirs('logs', exist_ok=True)
                    with open('logs/daily_reminders.txt', 'a') as f:
                        f.write(f"{datetime.now()}: Email sent to {user.email}\n")
                except:
                    pass
        
        return {
            'status': 'success',
            'task': 'daily_reminder',
            'executed_at': datetime.now().isoformat(),
            'users_notified': len(inactive_users),
            'emails': inactive_users
        }
    except Exception as e:
        print(f"Daily reminder failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery.task(bind=True, name='tasks.send_monthly_report')
def send_monthly_report(self):
    try:
        print("Starting monthly report generation")
        
        today = datetime.now()
        first_day_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if today.month == 1:
            last_month_start = first_day_this_month.replace(year=today.year - 1, month=12)
        else:
            last_month_start = first_day_this_month.replace(month=today.month - 1)
        
        last_month_end = first_day_this_month
        
        users = User.query.filter(~User.roles.any(name='admin')).all()
        
        reports_sent = []
        
        for user in users:
            bookings = Booking.query.filter(
                Booking.user_id == user.id,
                Booking.start_time >= last_month_start,
                Booking.start_time < last_month_end
            ).all()
            
            if not bookings:
                continue
            
            total_bookings = len(bookings)
            total_spent = sum(b.total_cost for b in bookings if b.status == 'Completed')
            
            lot_usage = {}
            for booking in bookings:
                spot = ParkingSpot.query.get(booking.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                lot_usage[lot.name] = lot_usage.get(lot.name, 0) + 1
            
            most_used_lot = max(lot_usage, key=lot_usage.get) if lot_usage else 'N/A'
            
            body = f"""Hi {user.username or user.email},

Here's your parking activity for {last_month_start.strftime('%B %Y')}:

📈 Statistics:
- Total Bookings: {total_bookings}
- Total Spent: Rs.{total_spent:.2f}
- Most Used Lot: {most_used_lot}

Thank you for choosing our parking service!

Best regards,
Parking Management Team"""
            
            booking_rows = ""
            for booking in bookings:
                spot = ParkingSpot.query.get(booking.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                booking_rows += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{lot.name}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">#{spot.spot_number}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">Rs.{booking.total_cost:.2f}</td>
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
                            <li style="padding: 5px 0;">💰 <strong>Total Spent:</strong> Rs.{total_spent:.2f}</li>
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
                reports_sent.append(user.email)
                os.makedirs('logs/monthly_reports', exist_ok=True)
                with open(f"logs/monthly_reports/{user.id}_{last_month_start.strftime('%Y_%m')}.txt", 'w') as f:
                    f.write(f"Report sent to {user.email} at {datetime.now()}\n")
            except:
                pass
        
        try:
            admin_email = ADMIN_EMAIL
            
            all_bookings = Booking.query.filter(
                Booking.start_time >= last_month_start,
                Booking.start_time < last_month_end
            ).all()
            
            total_system_bookings = len(all_bookings)
            total_revenue = sum(b.total_cost for b in all_bookings if b.status == 'Completed')
            total_users_active = len(reports_sent)
            
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
- Total Revenue: Rs.{total_revenue:.2f}
- Active Users: {total_users_active}
- Reports Sent: {len(reports_sent)}
- Most Popular Lot: {most_popular_lot}

Parking Management System"""
            
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
                                    <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #198754;">Rs.{total_revenue:.2f}</p>
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
            
            email_alert(admin_subject, admin_body, admin_email, admin_html)
            reports_sent.append(f"{admin_email} (admin)")
        except:
            pass
        
        return {
            'status': 'success',
            'task': 'monthly_report',
            'executed_at': datetime.now().isoformat(),
            'month': last_month_start.strftime('%B %Y'),
            'reports_sent': len(reports_sent),
            'emails': reports_sent
        }
    except Exception as e:
        print(f"Monthly report failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery.task(bind=True, name='tasks.export_user_bookings')
def export_user_bookings(self, user_id):
    try:
        user_id = int(user_id)
        print(f"Starting CSV generation for user {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}
        
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.start_time.desc()).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Booking ID', 'Parking Lot', 'Spot Number', 'Type', 'Start Time', 'End Time', 'Duration (hours)', 'Cost (Rs.)', 'Status'])
        
        for booking in bookings:
            spot = ParkingSpot.query.get(booking.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            
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
        
        os.makedirs('exports', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"exports/bookings_{user.id}_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())
        
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
                        <strong>📎 Attachment:</strong> The CSV file is attached to this email.
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
            from email.message import EmailMessage
            import smtplib
            
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['To'] = user.email
            msg['From'] = "nbhanuvardhanreddy@gmail.com"
            
            msg.set_content(body)
            msg.add_alternative(html, subtype='html')
            
            with open(filename, 'rb') as f:
                csv_data = f.read()
                msg.add_attachment(csv_data, maintype='text', subtype='csv', filename=f'booking_history_{timestamp}.csv')
            
            smtp_user = "nbhanuvardhanreddy@gmail.com"
            smtp_password = 'irsi znit bdyl hwcu'
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
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
        print(f"Export failed for user {user_id}: {str(e)}")
        return {'status': 'error', 'user_id': user_id, 'message': str(e)}


@celery.task(bind=True, name='tasks.send_booking_confirmation')
def send_booking_confirmation(self, booking_id):
    try:
        print(f"Sending booking confirmation for booking {booking_id}")
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return {'status': 'error', 'message': 'Booking not found'}
        
        user = User.query.get(booking.user_id)
        spot = ParkingSpot.query.get(booking.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        
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
- Total Cost: Rs.{booking.total_cost:.2f}
- Price Rate: Rs.{lot.price_per_hour}/hour

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
                                <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #0d6efd; font-size: 18px;"><strong>Rs.{booking.total_cost:.2f}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px;"><strong>Price Rate:</strong></td>
                                <td style="padding: 8px;">Rs.{lot.price_per_hour}/hour</td>
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
            subject = f"✅ Parking Confirmed - {lot.name} Spot #{spot.spot_number}"
            
            body = f"""Hi {user.username or user.email},

Your parking spot has been confirmed!

📋 Booking Details:
- Parking Lot: {lot.name}
- Spot Number: #{spot.spot_number}
- Start Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')}
- Price Rate: Rs.{lot.price_per_hour}/hour

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
                                <td style="padding: 8px;">Rs.{lot.price_per_hour}/hour</td>
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
        
        try:
            email_alert(subject, body, user.email, html)
            
            return {
                'status': 'success',
                'task': 'booking_confirmation',
                'booking_id': booking_id,
                'user_email': user.email,
                'executed_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'task': 'booking_confirmation',
                'booking_id': booking_id,
                'error': str(e)
            }
            
    except Exception as e:
        print(f"Booking confirmation failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery.task(bind=True, name='tasks.send_daily_admin_report')
def send_daily_admin_report(self):
    try:
        print("Generating daily admin report")
        
        admin_email = ADMIN_EMAIL
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        bookings_yesterday = Booking.query.filter(
            Booking.start_time >= yesterday,
            Booking.start_time < today
        ).all()
        
        total_bookings = len(bookings_yesterday)
        immediate_bookings = sum(1 for b in bookings_yesterday if b.booking_type == 'immediate')
        reserved_bookings = sum(1 for b in bookings_yesterday if b.booking_type == 'reserved')
        
        completed_yesterday = Booking.query.filter(
            Booking.end_time >= yesterday,
            Booking.end_time < today,
            Booking.status == 'Completed'
        ).all()
        
        revenue_yesterday = sum(b.total_cost for b in completed_yesterday)
        
        new_users = User.query.filter(~User.roles.any(name='admin')).count()
        
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status='Occupied').count()
        occupancy_rate = (occupied_spots / total_spots * 100) if total_spots > 0 else 0
        
        lot_bookings = {}
        for booking in bookings_yesterday:
            spot = ParkingSpot.query.get(booking.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            lot_bookings[lot.name] = lot_bookings.get(lot.name, 0) + 1
        
        most_popular_lot = max(lot_bookings, key=lot_bookings.get) if lot_bookings else 'N/A'
        most_popular_count = lot_bookings.get(most_popular_lot, 0) if lot_bookings else 0
        
        subject = f"📊 Daily Admin Report - {yesterday.strftime('%B %d, %Y')}"
        
        body = f"""Daily Parking System Report

Date: {yesterday.strftime('%B %d, %Y')}

📈 YESTERDAY'S ACTIVITY:
- Total Bookings: {total_bookings}
  • Immediate: {immediate_bookings}
  • Reserved: {reserved_bookings}
- Revenue Generated: Rs.{revenue_yesterday:.2f}
- New Users: {new_users}

🅿️ CURRENT STATUS:
- Occupancy Rate: {occupancy_rate:.1f}%
- Occupied Spots: {occupied_spots}/{total_spots}

🏆 TOP PERFORMER:
- Most Popular Lot: {most_popular_lot} ({most_popular_count} bookings)

Parking Management System
"""
        
        booking_rows = ""
        for booking in bookings_yesterday[:10]:
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
                            <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #198754;">Rs.{revenue_yesterday:.2f}
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
        
        try:
            email_alert(subject, body, admin_email, html)
            
            return {
                'status': 'success',
                'task': 'daily_admin_report',
                'date': yesterday.strftime('%Y-%m-%d'),
                'total_bookings': total_bookings,
                'revenue': float(revenue_yesterday),
                'admin_email': admin_email,
                'executed_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'task': 'daily_admin_report',
                'error': str(e)
            }
            
    except Exception as e:
        print(f"Daily admin report failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery.task(bind=True, name='tasks.export_admin_all_data')
def export_admin_all_data(self):
    try:
        print("Starting comprehensive data export")
        
        admin_email = ADMIN_EMAIL
        
        all_users = User.query.filter(~User.roles.any(name='admin')).all()
        all_lots = ParkingLot.query.all()
        all_spots = ParkingSpot.query.all()
        all_bookings = Booking.query.order_by(Booking.start_time.desc()).all()
        
        users_output = StringIO()
        users_writer = csv.writer(users_output)
        users_writer.writerow(['User ID', 'Email', 'Username', 'Total Bookings', 'Total Spent'])
        
        for user in all_users:
            total_bookings_count = Booking.query.filter_by(user_id=user.id).count()
            total_spent = db.session.query(func.sum(Booking.total_cost)).filter(
                Booking.user_id == user.id,
                Booking.status == 'Completed'
            ).scalar() or 0.0
            
            users_writer.writerow([user.id, user.email, user.username, total_bookings_count, f"{total_spent:.2f}"])
        
        lots_output = StringIO()
        lots_writer = csv.writer(lots_output)
        lots_writer.writerow(['Lot ID', 'Name', 'Capacity', 'Price Per Hour', 'Available Spots', 'Occupied Spots', 'Total Revenue'])
        
        for lot in all_lots:
            available_spots = sum(1 for spot in lot.spots if spot.status == 'Available')
            occupied_spots = sum(1 for spot in lot.spots if spot.status == 'Occupied')
            
            lot_spots = [spot.id for spot in lot.spots]
            lot_revenue = db.session.query(func.sum(Booking.total_cost)).filter(
                Booking.spot_id.in_(lot_spots),
                Booking.status == 'Completed'
            ).scalar() or 0.0
            
            lots_writer.writerow([lot.id, lot.name, lot.capacity, f"{lot.price_per_hour:.2f}", available_spots, occupied_spots, f"{lot_revenue:.2f}"])
        
        bookings_output = StringIO()
        bookings_writer = csv.writer(bookings_output)
        bookings_writer.writerow(['Booking ID', 'User Email', 'Parking Lot', 'Spot Number', 'Type', 'Start Time', 'End Time', 'Reserved Start', 'Reserved End', 'Duration (hours)', 'Cost (Rs.)', 'Status'])
        
        for booking in all_bookings:
            spot = ParkingSpot.query.get(booking.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            user = User.query.get(booking.user_id)
            
            if booking.end_time:
                duration = (booking.end_time - booking.start_time).total_seconds() / 3600
            elif booking.reserved_start and booking.reserved_end:
                duration = (booking.reserved_end - booking.reserved_start).total_seconds() / 3600
            else:
                duration = 'Ongoing'
            
            bookings_writer.writerow([
                booking.id, user.email, lot.name, spot.spot_number, booking.booking_type.capitalize(),
                booking.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                booking.end_time.strftime('%Y-%m-%d %H:%M:%S') if booking.end_time else 'N/A',
                booking.reserved_start.strftime('%Y-%m-%d %H:%M:%S') if booking.reserved_start else 'N/A',
                booking.reserved_end.strftime('%Y-%m-%d %H:%M:%S') if booking.reserved_end else 'N/A',
                f"{duration:.2f}" if isinstance(duration, float) else duration,
                f"{booking.total_cost:.2f}", booking.status
            ])
        
        os.makedirs('exports/admin', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        users_filename = f"exports/admin/users_{timestamp}.csv"
        lots_filename = f"exports/admin/lots_{timestamp}.csv"
        bookings_filename = f"exports/admin/bookings_{timestamp}.csv"
        
        with open(users_filename, 'w', newline='', encoding='utf-8') as f:
            f.write(users_output.getvalue())
        
        with open(lots_filename, 'w', newline='', encoding='utf-8') as f:
            f.write(lots_output.getvalue())
        
        with open(bookings_filename, 'w', newline='', encoding='utf-8') as f:
            f.write(bookings_output.getvalue())
        
        total_revenue = db.session.query(func.sum(Booking.total_cost)).filter(Booking.status == 'Completed').scalar() or 0.0
        
        total_bookings = len(all_bookings)
        total_users = len(all_users)
        total_lots = len(all_lots)
        total_spots_count = len(all_spots)
        
        subject = f"📊 Complete System Export - {datetime.now().strftime('%B %d, %Y')}"
        
        body = f"""Complete System Data Export

Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY STATISTICS:
- Total Users: {total_users}
- Total Parking Lots: {total_lots}
- Total Parking Spots: {total_spots_count}
- Total Bookings: {total_bookings}
- Total Revenue: Rs.{total_revenue:.2f}

ATTACHED FILES:
1. users_{timestamp}.csv - All user data
2. lots_{timestamp}.csv - All parking lot data
3. bookings_{timestamp}.csv - All booking data

All data exported successfully.

Parking Management System"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #0d6efd;">📊 Complete System Export</h2>
                <p style="color: #6c757d; font-size: 16px;">Export Date: <strong>{datetime.now().strftime('%B %d, %Y at %H:%M')}</strong></p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #198754;">📈 Summary Statistics</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                        <div style="background-color: white; padding: 15px; border-left: 4px solid #0d6efd; border-radius: 3px;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">Total Users</p>
                            <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #0d6efd;">{total_users}</p>
                        </div>
                        <div style="background-color: white; padding: 15px; border-left: 4px solid #ffc107; border-radius: 3px;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">Total Lots</p>
                            <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #ffc107;">{total_lots}</p>
                        </div>
                        <div style="background-color: white; padding: 15px; border-left: 4px solid #6c757d; border-radius: 3px;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">Total Spots</p>
                            <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #6c757d;">{total_spots_count}</p>
                        </div>
                        <div style="background-color: white; padding: 15px; border-left: 4px solid #dc3545; border-radius: 3px;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">Total Bookings</p>
                            <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: bold; color: #dc3545;">{total_bookings}</p>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 15px; background-color: #198754; color: white; border-radius: 3px; text-align: center;">
                        <p style="margin: 0; font-size: 14px;">Total Revenue Generated</p>
                        <p style="margin: 5px 0 0 0; font-size: 32px; font-weight: bold;">Rs.{total_revenue:.2f}</p>
                    </div>
                </div>
                
                <div style="background-color: #d1ecf1; border-left: 4px solid #0dcaf0; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #0c5460;">📎 Attached Files</h3>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li style="margin: 5px 0;"><strong>users_{timestamp}.csv</strong> - All user data with bookings and spending</li>
                        <li style="margin: 5px 0;"><strong>lots_{timestamp}.csv</strong> - All parking lot data with revenue</li>
                        <li style="margin: 5px 0;"><strong>bookings_{timestamp}.csv</strong> - Complete booking history</li>
                    </ul>
                </div>
                
                <p style="color: #6c757d; font-size: 14px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                    This is a complete system data export<br>
                    <strong>Parking Management System</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            from email.message import EmailMessage
            import smtplib
            
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['To'] = admin_email
            msg['From'] = "nbhanuvardhanreddy@gmail.com"
            
            msg.set_content(body)
            msg.add_alternative(html, subtype='html')
            
            with open(users_filename, 'rb') as f:
                msg.add_attachment(f.read(), maintype='text', subtype='csv', filename=f'users_{timestamp}.csv')
            
            with open(lots_filename, 'rb') as f:
                msg.add_attachment(f.read(), maintype='text', subtype='csv', filename=f'lots_{timestamp}.csv')
            
            with open(bookings_filename, 'rb') as f:
                msg.add_attachment(f.read(), maintype='text', subtype='csv', filename=f'bookings_{timestamp}.csv')
            
            smtp_user = "nbhanuvardhanreddy@gmail.com"
            smtp_password = 'irsi znit bdyl hwcu'
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {
                'status': 'success',
                'task': 'admin_export_all',
                'admin_email': admin_email,
                'total_users': total_users,
                'total_lots': total_lots,
                'total_spots': total_spots_count,
                'total_bookings': total_bookings,
                'total_revenue': float(total_revenue),
                'files': [users_filename, lots_filename, bookings_filename],
                'generated_at': datetime.now().isoformat(),
                'email_sent': True
            }
        except Exception as email_error:
            return {
                'status': 'success',
                'task': 'admin_export_all',
                'admin_email': admin_email,
                'total_users': total_users,
                'total_lots': total_lots,
                'total_bookings': total_bookings,
                'files': [users_filename, lots_filename, bookings_filename],
                'generated_at': datetime.now().isoformat(),
                'email_sent': False,
                'email_error': str(email_error)
            }
    except Exception as e:
        print(f"Admin export failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}
