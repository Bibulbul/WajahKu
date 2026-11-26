"""Database PostgreSQL kosong untuk test: schema baru per panggilan, dihapus saat proses test selesai."""
import atexit
import os
import uuid

import psycopg
from psycopg.conninfo import make_conninfo

from config import Config


def fresh_db():
    """URL koneksi ke schema kosong di TEST_DATABASE_URL (default: DATABASE_URL), supaya data asli tidak tersentuh."""
    url = os.environ.get('TEST_DATABASE_URL', Config.DATABASE)
    schema = f'tes_{uuid.uuid4().hex[:12]}'
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(f'CREATE SCHEMA {schema}')
    atexit.register(drop, url, schema)
    return make_conninfo(url, options=f'-csearch_path={schema}')


def drop(url, schema):
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(f'DROP SCHEMA {schema} CASCADE')
