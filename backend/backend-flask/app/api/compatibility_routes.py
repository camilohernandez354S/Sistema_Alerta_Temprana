"""
Rutas de compatibilidad para mantener la interfaz exacta del sistema anterior
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import jwt

# Crear blueprint para compatibilidad (sin prefijo para mantener rutas exactas)
compatibility_bp = Blueprint('compatibility', __name__)

@compatibility_bp.route('/api/login', methods=['POST'])
def login_compatibility():
    """
    Endpoint de compatibilidad EXACTA con /api/login del sistema anterior
    Mantiene exactamente la misma ruta, comportamiento y respuesta
    
    Body:
        username: string
        password: string
    
    Returns:
        200: {"mensaje": "Bienvenido admin", "token": "jwt_token", "rol": "admin"}
        401: {"error": "Credenciales incorrectas"}
        400: {"error": "Faltan datos"}
    """
    try:
        # Validación exactamente igual que antes
        data = request.get_json()
        username = data.get('username') if data else None
        password = data.get('password') if data else None
        
        if not username or not password:
            return jsonify({'error': 'Faltan datos'}), 400
        
        # Mismos usuarios del sistema anterior
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
        
        # Lógica de validación exactamente igual
        user = USUARIOS.get(username)
        if user and user['password'] == password:
            # JWT con la misma configuración que antes
            SECRET_KEY = 'supersecreto'  # Mismo secret
            
            payload = {
                'sub': username,
                'rol': user['rol'],
                'exp': datetime.utcnow() + timedelta(hours=2)  # Misma duración
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            
            # Respuesta exactamente igual que antes
            response = {
                'mensaje': f'Bienvenido {user["rol"]}',
                'token': token,
                'rol': user['rol']
            }
            
            current_app.logger.info(f"Login exitoso (compatibilidad) para: {username}")
            return jsonify(response), 200
        else:
            # Error exactamente igual que antes
            current_app.logger.warning(f"Login fallido (compatibilidad) para: {username}")
            return jsonify({'error': 'Credenciales incorrectas'}), 401
            
    except Exception as e:
        current_app.logger.error(f"Error en login compatibilidad: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@compatibility_bp.route('/api/verify-token', methods=['GET'])
def verify_token_compatibility():
    """
    Endpoint para verificar tokens del sistema anterior
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: {"valid": true, "user": {...}}
        401: {"valid": false, "error": "Token inválido"}
    """
    try:
        # Obtener token del header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'valid': False,
                'error': 'Token de autorización requerido'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verificar token con la misma configuración que antes
        SECRET_KEY = 'supersecreto'
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            # Respuesta de token válido
            return jsonify({
                'valid': True,
                'user': {
                    'username': payload.get('sub'),
                    'rol': payload.get('rol')
                }
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'valid': False,
                'error': 'Token expirado'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'valid': False,
                'error': 'Token inválido'
            }), 401
            
    except Exception as e:
        current_app.logger.error(f"Error verificando token compatibilidad: {e}")
        return jsonify({
            'valid': False,
            'error': 'Error interno del servidor'
        }), 500
