# user_routes.py
# Rutas protegidas para admin y usuario
from flask import jsonify, request
from .jwt_middleware import validar_jwt

def registrar_rutas_usuario(app):
    @app.route('/api/saludo-admin')
    @validar_jwt
    def saludo_admin():
        user = getattr(request, 'user', {})
        if user.get('rol') != 'admin':
            return jsonify({'error': 'No autorizado'}), 403
        return jsonify({'mensaje': f'Hola admin {user.get("sub")}, bienvenido al panel de administrador.'})

    @app.route('/api/saludo-usuario')
    @validar_jwt
    def saludo_usuario():
        user = getattr(request, 'user', {})
        if user.get('rol') != 'usuario':
            return jsonify({'error': 'No autorizado'}), 403
        return jsonify({'mensaje': f'Hola usuario {user.get("sub")}, bienvenido a tu panel.'})
