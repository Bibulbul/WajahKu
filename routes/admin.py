import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from database.db import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def require_admin(claims):
    return claims.get('role') == 'admin'


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    claims = get_jwt()
    if not require_admin(claims):
        return jsonify({'error': 'Akses ditolak'}), 403

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM scans")
        total_scans = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM products")
        total_products = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM product_reviews")
        total_reviews = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']

        cursor.execute("SELECT conditions_detected FROM scans")
        all_conditions = []
        for row in cursor.fetchall():
            all_conditions.extend(json.loads(row['conditions_detected']))

        condition_counts = {}
        for cond in all_conditions:
            condition_counts[cond] = condition_counts.get(cond, 0) + 1

        cursor.execute("""
            SELECT s.id, s.scan_date, s.conditions_detected, u.username, u.email
            FROM scans s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.scan_date DESC
            LIMIT 10
        """)
        recent_scans = []
        for row in cursor.fetchall():
            scan = dict(row)
            scan['conditions_detected'] = json.loads(scan['conditions_detected'])
            recent_scans.append(scan)
            
    except Exception as e:
        current_app.logger.error(f"Gagal mengambil statistik: {e}")
        return jsonify({'error': 'Terjadi kesalahan saat memuat data statistik'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({
        'total_scans': total_scans,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'total_users': total_users,
        'condition_distribution': condition_counts,
        'recent_scans': recent_scans
    }), 200


@admin_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    claims = get_jwt()
    if not require_admin(claims):
        return jsonify({'error': 'Akses ditolak'}), 403

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, COUNT(pr.id) as review_count
            FROM products p
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """)
        products = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        current_app.logger.error(f"Gagal memuat produk: {e}")
        return jsonify({'error': 'Terjadi kesalahan saat memuat produk'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify(products), 200


@admin_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    claims = get_jwt()
    if not require_admin(claims):
        return jsonify({'error': 'Akses ditolak'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data produk tidak disertakan'}), 400

    required_fields = ['name', 'brand', 'category', 'description', 'price', 'bpom_number']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Kolom {field} diperlukan'}), 400

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, brand, category, description, price, bpom_number, active_ingredients)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['name'],
            data['brand'],
            data['category'],
            data['description'],
            int(data['price']),
            data['bpom_number'],
            data.get('active_ingredients', '')
        ))
        product_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        current_app.logger.error(f"Gagal menambah produk: {e}")
        return jsonify({'error': 'Terjadi kesalahan saat menyimpan produk'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({'message': 'Produk berhasil ditambahkan', 'id': product_id}), 201


@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    claims = get_jwt()
    if not require_admin(claims):
        return jsonify({'error': 'Akses ditolak'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data produk tidak disertakan'}), 400

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Produk tidak ditemukan'}), 404

        cursor.execute("""
            UPDATE products 
            SET name = ?, brand = ?, category = ?, description = ?, 
                price = ?, bpom_number = ?, active_ingredients = ?
            WHERE id = ?
        """, (
            data.get('name'),
            data.get('brand'),
            data.get('category'),
            data.get('description'),
            int(data.get('price', 0)),
            data.get('bpom_number'),
            data.get('active_ingredients', ''),
            product_id
        ))
        conn.commit()
    except Exception as e:
        current_app.logger.error(f"Gagal mengupdate produk: {e}")
        return jsonify({'error': 'Terjadi kesalahan saat mengupdate produk'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({'message': 'Produk berhasil diperbarui'}), 200


@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    claims = get_jwt()
    if not require_admin(claims):
        return jsonify({'error': 'Akses ditolak'}), 403

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Produk tidak ditemukan'}), 404

        cursor.execute("DELETE FROM product_reviews WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    except Exception as e:
        current_app.logger.error(f"Gagal menghapus produk: {e}")
        return jsonify({'error': 'Terjadi kesalahan saat menghapus produk'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({'message': 'Produk berhasil dihapus'}), 200
