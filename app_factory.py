import os

from flask import Flask, jsonify

from config import config
from extensions import api, cors, db, jwt, migrate
from models import *  # noqa: F401,F403
from routes import blp


def create_app(config_name=None):
    app = Flask(__name__)
    selected_config = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config[selected_config])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    api.init_app(app)
    api.register_blueprint(blp)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Solicitud inválida", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "No autorizado", "message": str(error)}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "Acceso denegado", "message": str(error)}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "No encontrado", "message": str(error)}), 404

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({"error": "Conflicto", "message": str(error)}), 409

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Error interno", "message": "Ocurrió un error inesperado."}), 500

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token expirado", "message": "El token JWT ha expirado."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Token inválido", "message": "El token JWT no es válido."}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Token requerido", "message": "Se requiere un token JWT válido."}), 401

    with app.app_context():
        db.create_all()

    return app
