# auth_routes.py
# Rutas de autenticación
from flask import request, jsonify
from .auth_controller import AuthController

def registrar_rutas_auth(app):
    auth_controller = AuthController()

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'Faltan datos'}), 400
        resp, status = auth_controller.login(username, password)
        return jsonify(resp), status
