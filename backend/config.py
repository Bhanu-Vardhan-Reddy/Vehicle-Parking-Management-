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
