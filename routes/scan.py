import os
import uuid
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from PIL import Image

from database.db import get_db
from services.classifier import analyze_skin_image, SKIN_CONDITIONS

scan_bp = Blueprint('scan', __name__, url_prefix='/api')


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    )


@scan_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    user_id = int(get_jwt_identity())

    if 'photo' not in request.files:
        return jsonify({'error': 'Tidak ada foto yang diupload'}), 400

    file = request.files['photo']
    if not file or file.filename == '':
        return jsonify({'error': 'Tidak ada file yang dipilih'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Format file tidak didukung. Gunakan JPG, JPEG, atau PNG'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)

    try:
        file.save(filepath)
        img = Image.open(filepath)
        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        img.save(filepath, optimize=True, quality=85)
    except Exception as e:
        current_app.logger.error(f"Gagal menyimpan atau memproses gambar: {e}")
        return jsonify({'error': 'Gagal memproses file foto'}), 500

    try:
        conditions, recommendations = analyze_skin_image(filepath)
    except Exception as e:
        current_app.logger.error(f"Gagal menjalankan analisis: {e}")
        return jsonify({'error': 'Gagal menjalankan analisis kulit'}), 500

    relative_path = f"static/uploads/{filename}"

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO scans (user_id, photo_path, conditions_detected, confidence_scores, recommendations)
               VALUES (?, ?, ?, ?, ?)""",
            (
                user_id,
                relative_path,
                json.dumps(list(conditions.keys())),
                json.dumps({k: v['confidence'] for k, v in conditions.items()}),
                json.dumps(recommendations)
            )
        )
        scan_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        current_app.logger.error(f"Gagal menyimpan hasil scan ke database: {e}")
        return jsonify({'error': 'Gagal menyimpan hasil analisis'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({
        'scan_id': scan_id,
        'conditions': conditions,
        'recommendations': recommendations,
        'photo_path': relative_path
    }), 201


@scan_bp.route('/scans/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        if claims.get('role') == 'admin':
            cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        else:
            cursor.execute(
                "SELECT * FROM scans WHERE id = ? AND user_id = ?",
                (scan_id, user_id)
            )

        scan = cursor.fetchone()

        if not scan:
            return jsonify({'error': 'Scan tidak ditemukan'}), 404

        conditions_list = json.loads(scan['conditions_detected'])
        confidence_scores = json.loads(scan['confidence_scores'])
        recommendations = json.loads(scan['recommendations'])

        conditions = {}
        for cond in conditions_list:
            if cond in SKIN_CONDITIONS:
                conditions[cond] = {
                    'name': SKIN_CONDITIONS[cond]['name'],
                    'description': SKIN_CONDITIONS[cond]['description'],
                    'confidence': confidence_scores.get(cond, 0)
                }

        cursor.execute("""
            SELECT p.*,
                   COUNT(pr.id) as review_count,
                   COALESCE(AVG(pr.rating), 0) as avg_rating
            FROM products p
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            WHERE p.id IN (
                SELECT id FROM products ORDER BY RANDOM() LIMIT 6
            )
            GROUP BY p.id
            LIMIT 6
        """)
        products = [dict(row) for row in cursor.fetchall()]

    except Exception as e:
        current_app.logger.error(f"Gagal mengambil data scan: {e}")
        return jsonify({'error': 'Gagal memuat data scan'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({
        'scan': dict(scan),
        'conditions': conditions,
        'recommendations': recommendations,
        'products': products
    }), 200


@scan_bp.route('/history', methods=['GET'])
@jwt_required()
def api_history():
    user_id = int(get_jwt_identity())

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM scans WHERE user_id = ? ORDER BY scan_date DESC LIMIT 50",
            (user_id,)
        )
        scans = []
        for row in cursor.fetchall():
            scan_dict = dict(row)
            scan_dict['conditions_detected'] = json.loads(scan_dict['conditions_detected'])
            scan_dict['confidence_scores'] = json.loads(scan_dict['confidence_scores'])
            scans.append(scan_dict)
    except Exception as e:
        current_app.logger.error(f"Gagal mengambil riwayat scan: {e}")
        return jsonify({'error': 'Gagal memuat riwayat scan'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify(scans), 200
