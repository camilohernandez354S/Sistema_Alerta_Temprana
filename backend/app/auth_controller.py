# auth_controller.py
# Controlador para autenticación
from .auth_service import AuthService

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    def login(self, username, password):
        user = self.auth_service.validar_usuario(username, password)
        if user:
            token = self.auth_service.generar_jwt(user)
            return {
                'mensaje': f'Bienvenido {user["rol"]}',
                'token': token,
                'rol': user['rol']
            }, 200
        else:
            return {'error': 'Credenciales incorrectas'}, 401
