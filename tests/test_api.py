import io
import os
import shutil
import tempfile

from flask import Flask
from flask_jwt_extended import JWTManager

from config import Config
from database.db import init_db
from routes import auth
from routes.auth import auth_bp
from routes.scan import scan_bp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_app():
    """App dengan database dan folder upload sementara, supaya data asli tidak tersentuh."""
    tmp = tempfile.mkdtemp()
    for name in ('schema.sql', 'seed_data.sql'):
        shutil.copy(os.path.join(ROOT, 'database', name), tmp)
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(DATABASE=os.path.join(tmp, 'tes.db'), UPLOAD_FOLDER=os.path.join(tmp, 'uploads'))
    JWTManager(app)
    init_db(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(scan_bp)
    return app


def login(client, password, email='user@test.com'):
    return client.post('/api/auth/login', json={'email': email, 'password': password})


def test_login_limit():
    auth.failed_logins.clear()
    client = make_app().test_client()
    assert [login(client, 'salah').status_code for _ in range(5)] == [401] * 5
    assert login(client, 'user123').status_code == 429  # password benar pun ditolak sampai jendela lewat
    assert login(client, 'admin123', 'admin@test.com').status_code == 200  # email lain tidak ikut terkunci


def test_login_success_resets_count():
    auth.failed_logins.clear()
    client = make_app().test_client()
    for _ in range(4):
        login(client, 'salah')
    assert login(client, 'user123').status_code == 200
    assert [login(client, 'salah').status_code for _ in range(4)] == [401] * 4


def test_corrupt_upload_rejected_and_removed():
    auth.failed_logins.clear()
    app = make_app()
    client = app.test_client()
    token = login(client, 'user123').json['token']
    r = client.post('/api/upload', headers={'Authorization': f'Bearer {token}'},
                    data={'photo': (io.BytesIO(b'bukan gambar'), 'rusak.jpg')})
    assert r.status_code == 400, r.json
    assert os.listdir(app.config['UPLOAD_FOLDER']) == []


if __name__ == '__main__':
    test_login_limit(); test_login_success_resets_count(); test_corrupt_upload_rejected_and_removed()
    print('ok')
