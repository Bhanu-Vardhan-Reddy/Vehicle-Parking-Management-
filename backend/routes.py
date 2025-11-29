from flask import Blueprint, request, jsonify
from flask_security import hash_password
from flask_security.utils import verify_password
from models import db, User, Role
from datetime import datetime, timedelta, timezone
import jwt
from functools import wraps
import os

api_bp = Blueprint('api', __name__)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
cache = None

def init_cache(cache_instance):
    global cache
    cache = cache_instance

def generate_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'roles': [role.name for role in user.roles],
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing', 'error': 'unauthorized'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'User not found', 'error': 'unauthorized'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired', 'error': 'token_expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token', 'error': 'invalid_token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not any(role.name == 'admin' for role in current_user.roles):
            return jsonify({'message': 'Admin access required', 'error': 'forbidden'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required', 'error': 'validation_error'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User with this email already exists', 'error': 'user_exists'}), 400
    
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular user')
        db.session.add(user_role)
    
    import uuid
    new_user = User(
        email=data['email'],
        username=data.get('username', data['email'].split('@')[0]),
        password=hash_password(data['password']),
        fs_uniquifier=str(uuid.uuid4())
    )
    new_user.roles.append(user_role)
    
    db.session.add(new_user)
    db.session.commit()
    
    token = generate_token(new_user)
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': {
            'id': new_user.id,
            'email': new_user.email,
            'username': new_user.username,
            'roles': [role.name for role in new_user.roles]
        }
    }), 201

@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required', 'error': 'validation_error'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not verify_password(data['password'], user.password):
        return jsonify({'message': 'Invalid email or password', 'error': 'invalid_credentials'}), 401
    
    token = generate_token(user)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'roles': [role.name for role in user.roles]
        }
    }), 200

@api_bp.route('/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({
        'message': 'Token is valid',
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'username': current_user.username,
            'roles': [role.name for role in current_user.roles]
        }
    }), 200

@api_bp.route('/api/lots', methods=['GET'])
@token_required
def get_lots(current_user):
    from models import ParkingLot
    
    cached_data = cache.get('all_lots') if cache else None
    if cached_data:
        return jsonify(cached_data), 200
    
    lots = ParkingLot.query.all()
    result = {
        'lots': [{
            'id': lot.id,
            'name': lot.name,
            'capacity': lot.capacity,
            'price_per_hour': lot.price_per_hour,
            'available_spots': sum(1 for spot in lot.spots if spot.status == 'Available'),
            'occupied_spots': sum(1 for spot in lot.spots if spot.status == 'Occupied')
        } for lot in lots]
    }
    
    if cache:
        cache.set('all_lots', result, timeout=300)
    
    return jsonify(result), 200

@api_bp.route('/api/lots', methods=['POST'])
@token_required
@admin_required
def create_lot(current_user):
    from models import ParkingLot, ParkingSpot
    
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('capacity') or not data.get('price_per_hour'):
        return jsonify({'message': 'Name, capacity, and price_per_hour are required', 'error': 'validation_error'}), 400
    
    try:
        capacity = int(data['capacity'])
        price_per_hour = float(data['price_per_hour'])
        
        if capacity < 1:
            return jsonify({'message': 'Capacity must be at least 1', 'error': 'validation_error'}), 400
        if price_per_hour < 0:
            return jsonify({'message': 'Price must be non-negative', 'error': 'validation_error'}), 400
            
    except ValueError:
        return jsonify({'message': 'Invalid capacity or price format', 'error': 'validation_error'}), 400
    
    new_lot = ParkingLot(name=data['name'], capacity=capacity, price_per_hour=price_per_hour)
    db.session.add(new_lot)
    db.session.flush()
    
    for i in range(1, capacity + 1):
        spot = ParkingSpot(spot_number=i, status='Available', lot_id=new_lot.id)
        db.session.add(spot)
    
    db.session.commit()
    
    if cache:
        cache.delete('all_lots')
    
    return jsonify({
        'message': 'Parking lot created successfully',
        'lot': {'id': new_lot.id, 'name': new_lot.name, 'capacity': new_lot.capacity, 'price_per_hour': new_lot.price_per_hour}
    }), 201

@api_bp.route('/api/lots/<int:lot_id>', methods=['PUT'])
@token_required
@admin_required
def update_lot(current_user, lot_id):
    from models import ParkingLot, ParkingSpot
    
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Parking lot not found', 'error': 'not_found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided', 'error': 'validation_error'}), 400
    
    if data.get('name'):
        lot.name = data['name']
    
    if data.get('price_per_hour') is not None:
        try:
            price = float(data['price_per_hour'])
            if price < 0:
                return jsonify({'message': 'Price must be non-negative', 'error': 'validation_error'}), 400
            lot.price_per_hour = price
        except ValueError:
            return jsonify({'message': 'Invalid price format', 'error': 'validation_error'}), 400
    
    if data.get('capacity') is not None:
        try:
            new_capacity = int(data['capacity'])
            if new_capacity < 1:
                return jsonify({'message': 'Capacity must be at least 1', 'error': 'validation_error'}), 400
            
            current_capacity = lot.capacity
            
            if new_capacity > current_capacity:
                for i in range(current_capacity + 1, new_capacity + 1):
                    spot = ParkingSpot(spot_number=i, status='Available', lot_id=lot.id)
                    db.session.add(spot)
            
            elif new_capacity < current_capacity:
                spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id)\
                    .order_by(ParkingSpot.spot_number.desc())\
                    .limit(current_capacity - new_capacity).all()
                
                for spot in spots_to_remove:
                    if spot.status == 'Occupied':
                        return jsonify({
                            'message': f'Cannot reduce capacity: Spot #{spot.spot_number} is occupied',
                            'error': 'spot_occupied'
                        }), 400
                
                for spot in spots_to_remove:
                    db.session.delete(spot)
            
            lot.capacity = new_capacity
            
        except ValueError:
            return jsonify({'message': 'Invalid capacity format', 'error': 'validation_error'}), 400
    
    db.session.commit()
    
    if cache:
        cache.delete('all_lots')
        cache.delete(f'spots_lot_{lot_id}')
    
    return jsonify({
        'message': 'Parking lot updated successfully',
        'lot': {
            'id': lot.id,
            'name': lot.name,
            'capacity': lot.capacity,
            'price_per_hour': lot.price_per_hour
        }
    }), 200

@api_bp.route('/api/lots/<int:lot_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_lot(current_user, lot_id):
    from models import ParkingLot, Booking
    
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Parking lot not found', 'error': 'not_found'}), 404
    
    occupied_spots = sum(1 for spot in lot.spots if spot.status == 'Occupied')
    if occupied_spots > 0:
        return jsonify({'message': f'Cannot delete lot with {occupied_spots} occupied spot(s)', 'error': 'spots_occupied'}), 400
    
    spot_ids = [spot.id for spot in lot.spots]
    if spot_ids:
        Booking.query.filter(Booking.spot_id.in_(spot_ids)).delete(synchronize_session=False)
    
    db.session.delete(lot)
    db.session.commit()
    
    if cache:
        cache.delete('all_lots')
        cache.delete(f'spots_lot_{lot_id}')
    
    return jsonify({'message': 'Parking lot deleted successfully'}), 200

@api_bp.route('/api/spots/<int:lot_id>', methods=['GET'])
@token_required
def get_spots(current_user, lot_id):
    from models import ParkingLot, ParkingSpot, Booking
    
    cache_key = f'spots_lot_{lot_id}'
    cached_data = cache.get(cache_key) if cache else None
    if cached_data:
        return jsonify(cached_data), 200
    
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Parking lot not found', 'error': 'not_found'}), 404
    
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.spot_number).all()
    
    result_spots = []
    for spot in spots:
        spot_data = {'id': spot.id, 'spot_number': spot.spot_number, 'status': spot.status, 'reservations': []}
        
        bookings = Booking.query.filter(Booking.spot_id == spot.id, Booking.status.in_(['Active', 'Reserved'])).all()
        
        for booking in bookings:
            if booking.status == 'Reserved':
                spot_data['reservations'].append({
                    'start': booking.reserved_start.isoformat(),
                    'end': booking.reserved_end.isoformat(),
                    'user_email': booking.user.email if booking.user_id != current_user.id else 'You'
                })
        
        result_spots.append(spot_data)
    
    result = {'lot': {'id': lot.id, 'name': lot.name, 'price_per_hour': lot.price_per_hour}, 'spots': result_spots}
    
    if cache:
        cache.set(cache_key, result, timeout=60)
    
    return jsonify(result), 200

@api_bp.route('/api/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    from models import Booking
    
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'roles': [role.name for role in user.roles],
            'total_bookings': Booking.query.filter_by(user_id=user.id).count(),
            'active_bookings': Booking.query.filter_by(user_id=user.id, status='Active').count()
        } for user in users if not any(role.name == 'admin' for role in user.roles)]
    }), 200

@api_bp.route('/api/admin/bookings', methods=['GET'])
@token_required
@admin_required
def get_all_bookings(current_user):
    from models import Booking, ParkingSpot, ParkingLot
    
    status_filter = request.args.get('status')
    
    query = Booking.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    bookings = query.order_by(Booking.start_time.desc()).all()
    
    result = []
    for booking in bookings:
        spot = ParkingSpot.query.get(booking.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        user = User.query.get(booking.user_id)
        
        result.append({
            'id': booking.id,
            'user_email': user.email,
            'lot_name': lot.name,
            'spot_number': spot.spot_number,
            'booking_type': booking.booking_type,
            'start_time': booking.start_time.isoformat(),
            'end_time': booking.end_time.isoformat() if booking.end_time else None,
            'reserved_start': booking.reserved_start.isoformat() if booking.reserved_start else None,
            'reserved_end': booking.reserved_end.isoformat() if booking.reserved_end else None,
            'total_cost': booking.total_cost,
            'status': booking.status
        })
    
    return jsonify({'bookings': result}), 200

@api_bp.route('/api/stats/admin', methods=['GET'])
@token_required
@admin_required
def get_admin_stats(current_user):
    from models import ParkingLot, ParkingSpot, Booking
    from sqlalchemy import func
    
    total_revenue = db.session.query(func.sum(Booking.total_cost)).filter(Booking.status == 'Completed').scalar() or 0.0
    
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='Occupied').count()
    occupancy_rate = round((occupied_spots / total_spots * 100) if total_spots > 0 else 0, 2)
    
    lots = ParkingLot.query.all()
    revenue_by_lot = []
    for lot in lots:
        lot_spots = [spot.id for spot in lot.spots]
        lot_revenue = db.session.query(func.sum(Booking.total_cost)).filter(
            Booking.spot_id.in_(lot_spots), Booking.status == 'Completed'
        ).scalar() or 0.0
        revenue_by_lot.append({'lot_name': lot.name, 'revenue': float(lot_revenue)})
    
    active_bookings = Booking.query.filter_by(status='Active').count()
    reserved_bookings = Booking.query.filter_by(status='Reserved').count()
    completed_bookings = Booking.query.filter_by(status='Completed').count()
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'occupancy_rate': occupancy_rate,
        'revenue_by_lot': revenue_by_lot,
        'total_bookings': active_bookings + reserved_bookings + completed_bookings,
        'active_bookings': active_bookings,
        'reserved_bookings': reserved_bookings,
        'completed_bookings': completed_bookings
    }), 200

@api_bp.route('/api/stats/user', methods=['GET'])
@token_required
def get_user_stats(current_user):
    from models import Booking
    from sqlalchemy import func
    from dateutil.relativedelta import relativedelta
    
    total_spent = db.session.query(func.sum(Booking.total_cost)).filter(
        Booking.user_id == current_user.id, Booking.status == 'Completed'
    ).scalar() or 0.0
    
    now = datetime.now()
    monthly_data = []
    
    for i in range(5, -1, -1):
        month_date = now - relativedelta(months=i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if i == 0:
            month_end = now
        else:
            next_month = month_date + relativedelta(months=1)
            month_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        count = Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.start_time >= month_start,
            Booking.start_time < month_end
        ).count()
        
        spending = db.session.query(func.sum(Booking.total_cost)).filter(
            Booking.user_id == current_user.id,
            Booking.start_time >= month_start,
            Booking.start_time < month_end,
            Booking.status == 'Completed'
        ).scalar() or 0.0
        
        monthly_data.append({'month': month_date.strftime('%b %Y'), 'bookings': count, 'spending': float(spending)})
    
    return jsonify({'total_spent': float(total_spent), 'monthly_bookings': monthly_data}), 200

@api_bp.route('/api/export', methods=['GET'])
@token_required
def trigger_export(current_user):
    try:
        from tasks import export_user_bookings
        task = export_user_bookings.delay(current_user.id)
        return jsonify({'message': 'Export started! You will be notified when ready.', 'task_id': task.id, 'status': 'processing'}), 202
    except Exception as e:
        from models import Booking, ParkingSpot, ParkingLot
        import csv
        from io import StringIO
        
        bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
        
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
                booking.id, lot.name, spot.spot_number, booking.booking_type.capitalize(),
                booking.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                booking.end_time.strftime('%Y-%m-%d %H:%M:%S') if booking.end_time else 'N/A',
                f"{duration:.2f}" if isinstance(duration, float) else duration,
                f"{booking.total_cost:.2f}", booking.status
            ])
        
        os.makedirs('exports', exist_ok=True)
        filename = f"exports/bookings_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())
        
        return jsonify({'message': 'Export completed!', 'filename': filename, 'total_bookings': len(bookings)}), 200

@api_bp.route('/api/book', methods=['POST'])
@token_required
def book_spot(current_user):
    from models import ParkingLot, ParkingSpot, Booking
    from dateutil import parser
    
    data = request.get_json()
    
    if not data or not data.get('lot_id'):
        return jsonify({'message': 'lot_id is required', 'error': 'validation_error'}), 400
    
    booking_type = data.get('booking_type', 'immediate')
    spot_id = data.get('spot_id')
    
    if booking_type == 'immediate':
        active_booking = Booking.query.filter_by(user_id=current_user.id, status='Active').first()
        if active_booking:
            return jsonify({'message': 'You already have an active booking. Please release it first.', 'error': 'active_booking_exists'}), 400
    
    lot = ParkingLot.query.get(data['lot_id'])
    if not lot:
        return jsonify({'message': 'Parking lot not found', 'error': 'not_found'}), 404
    
    if booking_type == 'reserved':
        if not data.get('reserved_start') or not data.get('reserved_end'):
            return jsonify({'message': 'reserved_start and reserved_end are required for reservations', 'error': 'validation_error'}), 400
        
        try:
            reserved_start = parser.isoparse(data['reserved_start'])
            reserved_end = parser.isoparse(data['reserved_end'])
            
            if reserved_start.tzinfo is not None:
                reserved_start = reserved_start.astimezone(timezone.utc).replace(tzinfo=None)
            if reserved_end.tzinfo is not None:
                reserved_end = reserved_end.astimezone(timezone.utc).replace(tzinfo=None)
        except:
            return jsonify({'message': 'Invalid date format', 'error': 'validation_error'}), 400
        
        if reserved_start >= reserved_end:
            return jsonify({'message': 'End time must be after start time', 'error': 'validation_error'}), 400
        
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        if reserved_start < now_utc:
            return jsonify({'message': 'Start time cannot be in the past', 'error': 'validation_error'}), 400
        
        if spot_id:
            selected_spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot.id).first()
            if not selected_spot:
                return jsonify({'message': 'Invalid spot selection', 'error': 'not_found'}), 404
            
            conflicts = Booking.query.filter(
                Booking.spot_id == spot_id,
                Booking.status.in_(['Active', 'Reserved']),
                db.or_(
                    db.and_(Booking.reserved_start <= reserved_start, Booking.reserved_end > reserved_start),
                    db.and_(Booking.reserved_start < reserved_end, Booking.reserved_end >= reserved_end),
                    db.and_(Booking.reserved_start >= reserved_start, Booking.reserved_end <= reserved_end)
                )
            ).first()
            
            if conflicts:
                return jsonify({
                    'message': f'Spot #{selected_spot.spot_number} is already reserved',
                    'error': 'time_conflict',
                    'conflict': {'start': conflicts.reserved_start.isoformat(), 'end': conflicts.reserved_end.isoformat()}
                }), 400
            
            target_spot = selected_spot
        else:
            all_spots = ParkingSpot.query.filter_by(lot_id=lot.id).order_by(ParkingSpot.spot_number).all()
            target_spot = None
            
            for spot in all_spots:
                conflicts = Booking.query.filter(
                    Booking.spot_id == spot.id,
                    Booking.status.in_(['Active', 'Reserved']),
                    db.or_(
                        db.and_(Booking.reserved_start <= reserved_start, Booking.reserved_end > reserved_start),
                        db.and_(Booking.reserved_start < reserved_end, Booking.reserved_end >= reserved_end),
                        db.and_(Booking.reserved_start >= reserved_start, Booking.reserved_end <= reserved_end)
                    )
                ).first()
                
                if not conflicts:
                    target_spot = spot
                    break
            
            if not target_spot:
                return jsonify({'message': 'No spots available for the selected time period', 'error': 'no_spots_available'}), 400
        
        booking = Booking(
            user_id=current_user.id,
            spot_id=target_spot.id,
            booking_type='reserved',
            status='Reserved',
            reserved_start=reserved_start,
            reserved_end=reserved_end,
            start_time=reserved_start
        )
        
        duration_hours = (reserved_end - reserved_start).total_seconds() / 3600
        if duration_hours < 1:
            duration_hours = 1
        booking.total_cost = round(duration_hours * lot.price_per_hour, 2)
        
        db.session.add(booking)
        db.session.commit()
        
        if cache:
            cache.delete('all_lots')
            cache.delete(f'spots_lot_{lot.id}')
        
        try:
            from tasks import send_booking_confirmation
            send_booking_confirmation.delay(booking.id)
        except:
            pass
        
        return jsonify({
            'message': f'Successfully reserved Spot #{target_spot.spot_number}',
            'booking': {
                'id': booking.id,
                'spot_number': target_spot.spot_number,
                'lot_name': lot.name,
                'booking_type': 'reserved',
                'reserved_start': reserved_start.isoformat(),
                'reserved_end': reserved_end.isoformat(),
                'total_cost': booking.total_cost,
                'price_per_hour': lot.price_per_hour
            }
        }), 201
    
    else:
        if spot_id:
            selected_spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot.id, status='Available').first()
            if not selected_spot:
                return jsonify({'message': 'Selected spot is not available', 'error': 'spot_unavailable'}), 400
            target_spot = selected_spot
        else:
            target_spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='Available').order_by(ParkingSpot.spot_number).first()
            
            if not target_spot:
                return jsonify({'message': 'No available spots in this lot', 'error': 'no_spots_available'}), 400
        
        booking = Booking(
            user_id=current_user.id,
            spot_id=target_spot.id,
            start_time=datetime.now(),
            booking_type='immediate',
            status='Active'
        )
        
        target_spot.status = 'Occupied'
        
        db.session.add(booking)
        db.session.commit()
        
        if cache:
            cache.delete('all_lots')
            cache.delete(f'spots_lot_{lot.id}')
        
        try:
            from tasks import send_booking_confirmation
            send_booking_confirmation.delay(booking.id)
        except:
            pass
        
        return jsonify({
            'message': f'Successfully booked Spot #{target_spot.spot_number}',
            'booking': {
                'id': booking.id,
                'spot_number': target_spot.spot_number,
                'lot_name': lot.name,
                'booking_type': 'immediate',
                'start_time': booking.start_time.isoformat(),
                'price_per_hour': lot.price_per_hour
            }
        }), 201

@api_bp.route('/api/release/<int:booking_id>', methods=['POST'])
@token_required
def release_spot(current_user, booking_id):
    from models import Booking, ParkingSpot, ParkingLot
    
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'message': 'Booking not found', 'error': 'not_found'}), 404
    
    if booking.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized', 'error': 'unauthorized'}), 403
    
    if booking.status == 'Completed':
        return jsonify({'message': 'Booking already completed', 'error': 'already_completed'}), 400
    
    spot = ParkingSpot.query.get(booking.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)
    
    booking.end_time = datetime.now()
    duration_seconds = (booking.end_time - booking.start_time).total_seconds()
    duration_hours = duration_seconds / 3600
    
    if duration_hours < 1:
        duration_hours = 1
    
    booking.total_cost = round(duration_hours * lot.price_per_hour, 2)
    booking.status = 'Completed'
    spot.status = 'Available'
    
    db.session.commit()
    
    if cache:
        cache.delete('all_lots')
        cache.delete(f'spots_lot_{lot.id}')
    
    return jsonify({
        'message': 'Spot released successfully',
        'booking': {
            'id': booking.id,
            'spot_number': spot.spot_number,
            'lot_name': lot.name,
            'start_time': booking.start_time.isoformat(),
            'end_time': booking.end_time.isoformat(),
            'duration_hours': round(duration_hours, 2),
            'total_cost': booking.total_cost,
            'status': booking.status
        }
    }), 200

@api_bp.route('/api/bookings', methods=['GET'])
@token_required
def get_bookings(current_user):
    from models import Booking, ParkingSpot, ParkingLot
    
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
    
    result = []
    for booking in bookings:
        spot = ParkingSpot.query.get(booking.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        
        result.append({
            'id': booking.id,
            'lot_name': lot.name,
            'spot_number': spot.spot_number,
            'booking_type': booking.booking_type,
            'start_time': booking.start_time.isoformat(),
            'end_time': booking.end_time.isoformat() if booking.end_time else None,
            'reserved_start': booking.reserved_start.isoformat() if booking.reserved_start else None,
            'reserved_end': booking.reserved_end.isoformat() if booking.reserved_end else None,
            'total_cost': booking.total_cost,
            'status': booking.status
        })
    
    return jsonify({'bookings': result}), 200

@api_bp.route('/api/admin/send-daily-reminder', methods=['POST'])
@token_required
@admin_required
def trigger_daily_reminder(current_user):
    try:
        from tasks import send_daily_reminder
        task = send_daily_reminder.delay()
        return jsonify({'message': 'Daily reminder emails queued!', 'task_id': task.id, 'status': 'processing'}), 202
    except Exception as e:
        return jsonify({'message': f'Failed: {str(e)}', 'error': 'task_failed'}), 500

@api_bp.route('/api/admin/send-monthly-report', methods=['POST'])
@token_required
@admin_required
def trigger_monthly_report(current_user):
    try:
        from tasks import send_monthly_report
        task = send_monthly_report.delay()
        return jsonify({'message': 'Monthly report emails queued!', 'task_id': task.id, 'status': 'processing'}), 202
    except Exception as e:
        return jsonify({'message': f'Failed: {str(e)}', 'error': 'task_failed'}), 500

@api_bp.route('/api/admin/export-all', methods=['POST'])
@token_required
@admin_required
def trigger_admin_export(current_user):
    try:
        from tasks import export_admin_all_data
        task = export_admin_all_data.delay()
        return jsonify({'message': 'Data export started! Check your email.', 'task_id': task.id, 'status': 'processing'}), 202
    except Exception as e:
        return jsonify({'message': f'Failed: {str(e)}', 'error': 'task_failed'}), 500
