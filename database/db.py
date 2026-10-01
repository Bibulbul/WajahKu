import sqlite3
import os
from werkzeug.security import generate_password_hash
from flask import current_app

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db(app):
    """Initialize database with schema and seed data"""
    db_dir = os.path.dirname(app.config['DATABASE'])
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    with app.app_context():
        conn = get_db()
        
        # Execute schema
        schema_path = os.path.join(db_dir, 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
        
        cursor = conn.cursor()
        
        # Check if data exists
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            # Execute seed data
            seed_path = os.path.join(db_dir, 'seed_data.sql')
            if os.path.exists(seed_path):
                with open(seed_path, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
        
        # Check if test users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Create test accounts
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, ('testuser', 'user@test.com', generate_password_hash('user123'), 'user'))
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, ('admin', 'admin@test.com', generate_password_hash('admin123'), 'admin'))
        
        conn.commit()
        conn.close()
