import os
from datetime import timedelta

# Kunci ini tertulis di repo publik: hanya untuk development, ditolak di production
DEV_KEY = 'wajahku-secret-key-2024-change-in-production'


def secret(name, production):
    value = os.environ.get(name)
    if production and value in (None, '', DEV_KEY):
        raise RuntimeError(f'{name} wajib diisi dengan kunci acak saat APP_ENV=production')
    return value or DEV_KEY


class Config:
    # APP_ENV=production di server deploy: kunci wajib dari environment, tanpa debug dan tanpa akun uji
    PRODUCTION = os.environ.get('APP_ENV') == 'production'
    DEBUG = not PRODUCTION

    SECRET_KEY = secret('SECRET_KEY', PRODUCTION)
    JWT_SECRET_KEY = secret('JWT_SECRET_KEY', PRODUCTION)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max

    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'wajahku.db')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
