# auth_service.py
# Servicio para autenticación y generación de JWT
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'supersecreto'  # Cambia esto en producción
USUARIOS = {
    'admin': {
        'password': 'admin123',
        'rol': 'admin'
    },
    'usuario': {
        'password': 'usuario123',
        'rol': 'usuario'
    }
}

class AuthService:
    def validar_usuario(self, username, password):
        user = USUARIOS.get(username)
        if user and user['password'] == password:
            return {'username': username, 'rol': user['rol']}
        return None

    def generar_jwt(self, user):
        payload = {
            'sub': user['username'],
            'rol': user['rol'],
            'exp': datetime.utcnow() + timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
