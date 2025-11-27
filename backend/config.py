import os

# Get the base directory (backend folder)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # Database - absolute path to instance folder inside backend
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "parking.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Security
    SECURITY_PASSWORD_SALT = 'super-secret-salt'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    
    # Redis Caching - Milestone 7
    CACHE_TYPE = 'SimpleCache'  # Fallback to SimpleCache if Redis not available
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Redis configuration (will use if Redis is available)
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    
    # Celery Configuration - Milestone 8 (New lowercase format)
    broker_url = 'redis://127.0.0.1:6379/0'
    result_backend = 'redis://127.0.0.1:6379/0'
    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    timezone = 'UTC'
    enable_utc = True
