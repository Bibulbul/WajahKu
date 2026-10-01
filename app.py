from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config
from database.db import init_db
from routes.auth import auth_bp
from routes.scan import scan_bp
from routes.admin import admin_bp
from routes.products import products_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inisialisasi CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Serve uploads static directory (allow CORS on it for frontend images)
    import os
    from flask import send_from_directory
    @app.route('/static/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Inisialisasi JWT
    JWTManager(app)

    # Inisialisasi Database & Data awal
    init_db(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(products_bp)

    # Error Handling Global
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Endpoint tidak ditemukan'}), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({'error': 'Ukuran file melebihi batas maksimal (5MB)'}), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Terjadi kesalahan internal pada server'}), 500

    return app


app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("WajahKu.id - Backend API Server (Modular)")
    print("=" * 60)
    print("Server Berjalan di: http://localhost:5000")
    print("Endpoints API: /api/auth, /api/scans, /api/admin, /api/products")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
