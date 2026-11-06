import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = {'SECRET_KEY': 'acak-1', 'JWT_SECRET_KEY': 'acak-2'}


def run(code, **env):
    """Jalankan code di proses baru, karena Config dibaca sekali saat import."""
    clean = {k: v for k, v in os.environ.items() if k not in ('APP_ENV', 'SECRET_KEY', 'JWT_SECRET_KEY')}
    return subprocess.run([sys.executable, '-c', code], cwd=ROOT, env={**clean, **env},
                          capture_output=True, text=True)


def test_production_needs_keys():
    assert run('import config', APP_ENV='production').returncode != 0
    old = 'wajahku-secret-key-2024-change-in-production'
    assert run('import config', APP_ENV='production', SECRET_KEY=old, JWT_SECRET_KEY=old).returncode != 0


def test_production_no_debug_no_test_accounts():
    code = '''
import tempfile, shutil, os
from flask import Flask
from config import Config
from database.db import init_db, get_db
d = tempfile.mkdtemp()
for f in ('schema.sql', 'seed_data.sql'):
    shutil.copy(os.path.join('database', f), d)
app = Flask(__name__); app.config.from_object(Config); app.config['DATABASE'] = os.path.join(d, 'tes.db')
init_db(app)
with app.app_context():
    print(app.config['DEBUG'], get_db().execute('SELECT COUNT(*) FROM users').fetchone()[0])
'''
    assert run(code, APP_ENV='production', **KEYS).stdout.split() == ['False', '0']
    assert run(code).stdout.split() == ['True', '2']


if __name__ == '__main__':
    test_production_needs_keys(); test_production_no_debug_no_test_accounts()
    print('ok')
