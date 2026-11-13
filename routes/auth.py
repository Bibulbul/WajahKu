import time

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Batas tebak password: 5 kali salah per (IP, email) dalam 15 menit
LOGIN_LIMIT = 5
LOGIN_WINDOW = 15 * 60
# shortcut: disimpan di memori per proses (hilang saat restart, tidak dibagi antar worker), pindah ke database/Redis kalau server memakai banyak worker
failed_logins = {}


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email dan password diperlukan'}), 400

    email = data['email'].strip().lower()
    password = data['password']
    username = data.get('username', email.split('@')[0]).strip()

    if len(password) < 6:
        return jsonify({'error': 'Password minimal 6 karakter'}), 400

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email sudah terdaftar'}), 409

        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, 'user')
        )
        user_id = cursor.lastrowid
        conn.commit()
    except Exception:
        return jsonify({'error': 'Terjadi kesalahan, silakan coba lagi'}), 500
    finally:
        if conn:
            conn.close()

    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={'role': 'user', 'email': email}
    )

    return jsonify({
        'message': 'Registrasi berhasil',
        'token': access_token,
        'user': {
            'id': user_id,
            'email': email,
            'username': username,
            'role': 'user'
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email dan password diperlukan'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    now = time.time()
    key = (request.remote_addr, email)
    recent = [t for t in failed_logins.get(key, []) if now - t < LOGIN_WINDOW]
    if len(recent) >= LOGIN_LIMIT:
        return jsonify({'error': 'Terlalu banyak percobaan login. Coba lagi dalam 15 menit.'}), 429

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
    except Exception:
        return jsonify({'error': 'Terjadi kesalahan, silakan coba lagi'}), 500
    finally:
        if conn:
            conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        failed_logins[key] = recent + [now]
        if len(failed_logins) > 10000:  # buang catatan lama supaya memori tidak terus bertambah
            for k in [k for k, ts in failed_logins.items() if now - ts[-1] >= LOGIN_WINDOW]:
                del failed_logins[k]
        return jsonify({'error': 'Email atau password salah'}), 401

    failed_logins.pop(key, None)

    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims={'role': user['role'], 'email': user['email']}
    )

    return jsonify({
        'token': access_token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'username': user['username'],
            'role': user['role']
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, role, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
    except Exception:
        return jsonify({'error': 'Terjadi kesalahan, silakan coba lagi'}), 500
    finally:
        if conn:
            conn.close()

    if not user:
        return jsonify({'error': 'Pengguna tidak ditemukan'}), 404

    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'created_at': user['created_at']
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logout berhasil'}), 200
