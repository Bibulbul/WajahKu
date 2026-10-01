from flask import Blueprint, jsonify, current_app
from database.db import get_db

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('/<int:product_id>/reviews', methods=['GET'])
def product_reviews(product_id):
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Produk tidak ditemukan'}), 404

        cursor.execute("""
            SELECT * FROM product_reviews 
            WHERE product_id = ? 
            ORDER BY review_date DESC
        """, (product_id,))
        reviews = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        current_app.logger.error(f"Gagal mengambil ulasan produk: {e}")
        return jsonify({'error': 'Terjadi kesalahan saat memuat ulasan'}), 500
    finally:
        if conn:
            conn.close()

    return jsonify(reviews), 200
