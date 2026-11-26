import os
import psycopg
from psycopg.rows import dict_row
from psycopg.types.numeric import FloatLoader
from psycopg.types.string import TextLoader
from werkzeug.security import generate_password_hash
from flask import current_app

SQL_DIR = os.path.dirname(os.path.abspath(__file__))

# Frontend (parseScanDate) membaca waktu sebagai teks "YYYY-MM-DD HH:MM:SS" UTC, dan AVG() jadi angka, bukan Decimal
psycopg.adapters.register_loader('timestamp', TextLoader)
psycopg.adapters.register_loader('numeric', FloatLoader)


def get_db():
    """Get database connection"""
    return psycopg.connect(current_app.config['DATABASE'], row_factory=dict_row)


def read_sql(name):
    with open(os.path.join(SQL_DIR, name), 'r', encoding='utf-8') as f:
        return f.read()


def init_db(app):
    """Initialize database with schema and seed data"""
    with app.app_context():
        conn = get_db()

        # Server production bisa menjalankan beberapa worker sekaligus: init_db antre supaya seed tidak dobel
        conn.execute("SELECT pg_advisory_xact_lock(20241)")

        # Execute schema
        conn.execute(read_sql('schema.sql'))

        # Check if data exists
        if conn.execute("SELECT COUNT(*) AS n FROM products").fetchone()['n'] == 0:
            conn.execute(read_sql('seed_data.sql'))

        # Produk tambahan dari tim ML (salinan ml/data/produk_tambahan.sql). Seed di atas hanya jalan
        # untuk database kosong, jadi produk yang nomor BPOM-nya belum ada dimasukkan di sini.
        conn.execute("CREATE TEMP TABLE new_products ON COMMIT DROP AS SELECT * FROM products WITH NO DATA")
        conn.execute(read_sql('produk_tambahan.sql').replace('INSERT INTO products', 'INSERT INTO new_products', 1))
        conn.execute("""
            INSERT INTO products (name, brand, category, description, price, bpom_number, bpom_verified, active_ingredients)
            SELECT name, brand, category, description, price, bpom_number, bpom_verified, active_ingredients
            FROM new_products WHERE bpom_number NOT IN (SELECT bpom_number FROM products)
        """)

        # Check if test users exist (akun uji tidak dibuat di production: passwordnya tertulis di repo)
        no_users = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()['n'] == 0
        if not app.config['PRODUCTION'] and no_users:
            # Create test accounts
            conn.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
            """, ('testuser', 'user@test.com', generate_password_hash('user123'), 'user',
                  'admin', 'admin@test.com', generate_password_hash('admin123'), 'admin'))

        conn.commit()
        conn.close()
