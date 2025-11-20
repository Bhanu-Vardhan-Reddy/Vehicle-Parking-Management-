"""
API Routes for Vehicle Parking System
Milestone 2: Authentication & RBAC (Role-Based Access Control)
"""
from flask import Blueprint, request, jsonify
from flask_security import hash_password
from flask_security.utils import verify_password
from models import db, User, Role
from datetime import datetime, timedelta
import jwt
from functools import wraps
import os

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Secret key for JWT
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# ==========================================
# JWT Helper Functions
# ==========================================

def generate_token(user):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'roles': [role.name for role in user.roles],
        'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 24 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    """Decorator to protect routes - requires valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing', 'error': 'unauthorized'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'User not found', 'error': 'unauthorized'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired', 'error': 'token_expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token', 'error': 'invalid_token'}), 401
        
        # Pass current_user to the route
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to ensure user has admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Check if user has admin role
        if not any(role.name == 'admin' for role in current_user.roles):
            return jsonify({'message': 'Admin access required', 'error': 'forbidden'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ==========================================
# Authentication Endpoints
# ==========================================

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user (not admin)
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "password123",
        "username": "John Doe" (optional)
    }
    """
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            'message': 'Email and password are required',
            'error': 'validation_error'
        }), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'message': 'User with this email already exists',
            'error': 'user_exists'
        }), 400
    
    # Get or create 'user' role
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular user')
        db.session.add(user_role)
    
    # Create new user
    import uuid
    new_user = User(
        email=data['email'],
        username=data.get('username', data['email'].split('@')[0]),
        password=hash_password(data['password']),
        fs_uniquifier=str(uuid.uuid4()),
        active=True
    )
    new_user.roles.append(user_role)
    
    db.session.add(new_user)
    db.session.commit()
    
    # Generate token
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
    """
    Login for both admin and users
    
    Request Body:
    {
        "email": "admin@parking.com",
        "password": "admin123"
    }
    """
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            'message': 'Email and password are required',
            'error': 'validation_error'
        }), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    # Verify credentials
    if not user or not verify_password(data['password'], user.password):
        return jsonify({
            'message': 'Invalid email or password',
            'error': 'invalid_credentials'
        }), 401
    
    # Check if user is active
    if not user.active:
        return jsonify({
            'message': 'User account is inactive',
            'error': 'inactive_account'
        }), 401
    
    # Generate token
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
    """
    Verify if token is valid and return user info
    
    Headers:
    Authorization: Bearer <token>
    """
    return jsonify({
        'message': 'Token is valid',
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'username': current_user.username,
            'roles': [role.name for role in current_user.roles]
        }
    }), 200

# ==========================================
# Test Endpoints (Protected Routes)
# ==========================================

@api_bp.route('/test/protected', methods=['GET'])
@token_required
def test_protected(current_user):
    """Test endpoint - requires authentication"""
    return jsonify({
        'message': f'Hello {current_user.email}! This is a protected route.',
        'user_id': current_user.id,
        'roles': [role.name for role in current_user.roles]
    }), 200

@api_bp.route('/test/admin', methods=['GET'])
@token_required
@admin_required
def test_admin(current_user):
    """Test endpoint - requires admin role"""
    return jsonify({
        'message': f'Hello Admin {current_user.email}! You have admin access.',
        'user_id': current_user.id
    }), 200

# ==========================================
# Parking Lot Endpoints (Admin) - Milestone 3
# ==========================================

@api_bp.route('/api/lots', methods=['GET'])
@token_required
def get_lots(current_user):
    """Get all parking lots"""
    from models import ParkingLot
    
    lots = ParkingLot.query.all()
    return jsonify({
        'lots': [{
            'id': lot.id,
            'name': lot.name,
            'capacity': lot.capacity,
            'price_per_hour': lot.price_per_hour,
            'available_spots': sum(1 for spot in lot.spots if spot.status == 'Available'),
            'occupied_spots': sum(1 for spot in lot.spots if spot.status == 'Occupied')
        } for lot in lots]
    }), 200

@api_bp.route('/api/lots', methods=['POST'])
@token_required
@admin_required
def create_lot(current_user):
    """Create a new parking lot with auto-generated spots (Admin only)"""
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
    
    # Create parking lot
    new_lot = ParkingLot(
        name=data['name'],
        capacity=capacity,
        price_per_hour=price_per_hour
    )
    db.session.add(new_lot)
    db.session.flush()  # Get the lot ID before creating spots
    
    # Auto-create parking spots (1 to N)
    for i in range(1, capacity + 1):
        spot = ParkingSpot(
            spot_number=i,
            status='Available',
            lot_id=new_lot.id
        )
        db.session.add(spot)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Parking lot created successfully',
        'lot': {
            'id': new_lot.id,
            'name': new_lot.name,
            'capacity': new_lot.capacity,
            'price_per_hour': new_lot.price_per_hour
        }
    }), 201

@api_bp.route('/api/lots/<int:lot_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_lot(current_user, lot_id):
    """Delete a parking lot (Admin only, only if all spots are available)"""
    from models import ParkingLot
    
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Parking lot not found', 'error': 'not_found'}), 404
    
    # Check if any spot is occupied
    occupied_spots = sum(1 for spot in lot.spots if spot.status == 'Occupied')
    if occupied_spots > 0:
        return jsonify({
            'message': f'Cannot delete lot with {occupied_spots} occupied spot(s)',
            'error': 'spots_occupied'
        }), 400
    
    db.session.delete(lot)
    db.session.commit()
    
    return jsonify({'message': 'Parking lot deleted successfully'}), 200

@api_bp.route('/api/spots/<int:lot_id>', methods=['GET'])
@token_required
def get_spots(current_user, lot_id):
    """Get all parking spots for a specific lot"""
    from models import ParkingLot, ParkingSpot
    
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Parking lot not found', 'error': 'not_found'}), 404
    
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.spot_number).all()
    return jsonify({
        'lot': {
            'id': lot.id,
            'name': lot.name,
            'price_per_hour': lot.price_per_hour
        },
        'spots': [{
            'id': spot.id,
            'spot_number': spot.spot_number,
            'status': spot.status
        } for spot in spots]
    }), 200

@api_bp.route('/api/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    """Get all registered users (Admin only)"""
    from models import Booking
    
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'active': user.active,
            'roles': [role.name for role in user.roles],
            'total_bookings': Booking.query.filter_by(user_id=user.id).count(),
            'active_bookings': Booking.query.filter_by(user_id=user.id, status='Active').count()
        } for user in users if not any(role.name == 'admin' for role in user.roles)]
    }), 200

