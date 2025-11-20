"""
Flask Application Entry Point
Milestone 1: Database Models and Admin Seeding
"""
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from config import Config
from models import db, User, Role
import os

def create_app(config_class=Config):
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    
    with app.app_context():
        # Create instance directory if it doesn't exist
        instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        # Create all database tables
        db.create_all()
        
        # Seed admin user if not exists
        if not user_datastore.find_user(email='admin@parking.com'):
            # Create roles
            admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
            user_role = user_datastore.find_or_create_role(name='user', description='Regular user')
            
            # Create admin user
            admin_user = user_datastore.create_user(
                email='admin@parking.com',
                username='admin',
                password=hash_password('admin123'),
                active=True,
                roles=[admin_role]
            )
            db.session.commit()
            print('✅ Database initialized successfully!')
            print('✅ Admin user created: admin@parking.com / admin123')
        else:
            print('✅ Database already initialized!')
    
    # Simple test route
    @app.route('/')
    def index():
        return '''
        <h1>🚗 Vehicle Parking System</h1>
        <p>Milestone 1: Database Models ✅</p>
        <p>Database initialized with 5 tables:</p>
        <ul>
            <li>User</li>
            <li>Role</li>
            <li>ParkingLot</li>
            <li>ParkingSpot</li>
            <li>Booking</li>
        </ul>
        <p>Admin user: admin@parking.com / admin123</p>
        '''
    
    return app

if __name__ == '__main__':
    app = create_app()
    print('\n' + '='*50)
    print('🚀 Starting Flask Application')
    print('='*50)
    print('📍 Access at: http://localhost:5000')
    print('='*50 + '\n')
    app.run(debug=True, host='0.0.0.0', port=5000)
