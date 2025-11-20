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

