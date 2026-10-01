import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'wajahku-secret-key-2024-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'wajahku-secret-key-2024-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max
    
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'wajahku.db')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
