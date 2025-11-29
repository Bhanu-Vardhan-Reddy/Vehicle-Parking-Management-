from flask import Flask
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_caching import Cache
from config import Config
from models import db, User, Role
import os

cache = Cache()
celery = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app)
    
    try:
        app.config['CACHE_TYPE'] = 'redis'
        cache.init_app(app)
    except:
        app.config['CACHE_TYPE'] = 'SimpleCache'
        cache.init_app(app)
    
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    with app.app_context():
        db.create_all()
        
        if not user_datastore.find_user(email='nbhanuvardhanreddy@gmail.com'):
            admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
            user_datastore.find_or_create_role(name='user', description='Regular user')
            
            user_datastore.create_user(
                email='nbhanuvardhanreddy@gmail.com',
                username='admin',
                password=hash_password('admin123'),
                roles=[admin_role]
            )
            db.session.commit()
    
    from routes import api_bp, init_cache
    app.register_blueprint(api_bp)
    init_cache(cache)
    
    @app.route('/')
    def index():
        return '<h1>Vehicle Parking System API</h1><p>Status: Running</p>'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
