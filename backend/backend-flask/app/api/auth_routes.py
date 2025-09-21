"""
Rutas de autenticación
"""
from flask import Blueprint, request, jsonify, current_app
from http import HTTPStatus
from pymongo import MongoClient
import os

from app.models.user_model import UserLogin
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.utils.rate_limiter import auth_rate_limit, strict_rate_limit

# Crear blueprint
auth_bp = Blueprint('auth', __name__)

def get_auth_service():
    """Obtener instancia del servicio de autenticación"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB', 'sensor_database')
    
    client = MongoClient(mongo_uri)
    user_repository = UserRepository(client, db_name)
    return AuthService(user_repository)

@auth_bp.route('/login', methods=['POST'])
@auth_rate_limit()
def login():
    """
    Endpoint para autenticación de usuarios
    
    Body:
        username: string (usuario o email)
        password: string
    
    Returns:
        200: Login exitoso
        401: Credenciales incorrectas
        400: Datos inválidos
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos de entrada requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar campos requeridos
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Usuario y contraseña son requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        # Crear modelo de login
        login_data = UserLogin(username=username, password=password)
        
        # Obtener servicio de autenticación
        auth_service = get_auth_service()
        
        # Autenticar usuario
        token_response = auth_service.authenticate_user(login_data)
        
        if not token_response:
            current_app.logger.warning(f"Intento de login fallido para usuario: {username}")
            return jsonify({
                'success': False,
                'message': 'Credenciales incorrectas'
            }), HTTPStatus.UNAUTHORIZED
        
        # Generar refresh token
        refresh_token = auth_service._generate_refresh_token()
        
        # Almacenar refresh token
        if not auth_service.store_refresh_token(token_response.user.id, refresh_token):
            current_app.logger.error("Error almacenando refresh token")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        # Respuesta exitosa
        current_app.logger.info(f"Login exitoso para usuario: {username}")
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'access_token': token_response.access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': token_response.expires_in,
            'user': {
                'id': token_response.user.id,
                'username': token_response.user.username,
                'email': token_response.user.email,
                'full_name': token_response.user.full_name,
                'role': token_response.user.role,
                'location': token_response.user.location
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de login: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    Endpoint para verificar token de autenticación
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Token válido
        401: Token inválido o expirado
    """
    try:
        # Obtener token del header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Token de autorización requerido'
            }), HTTPStatus.UNAUTHORIZED
        
        token = auth_header.split(' ')[1]
        
        # Obtener servicio de autenticación
        auth_service = get_auth_service()
        
        # Verificar token
        user = auth_service.get_current_user(token)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Token inválido o expirado'
            }), HTTPStatus.UNAUTHORIZED
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Token válido',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'location': user.location
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error verificando token: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@auth_bp.route('/users', methods=['GET'])
def get_users():
    """
    Endpoint para obtener lista de usuarios (solo admin)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Lista de usuarios
        401: Token inválido o sin permisos
        403: Sin permisos de administrador
    """
    try:
        # Obtener token del header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Token de autorización requerido'
            }), HTTPStatus.UNAUTHORIZED
        
        token = auth_header.split(' ')[1]
        
        # Obtener servicio de autenticación
        auth_service = get_auth_service()
        
        # Verificar token y permisos de admin
        user = auth_service.get_current_user(token)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Token inválido o expirado'
            }), HTTPStatus.UNAUTHORIZED
        
        # Verificar que sea administrador
        if user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Permisos de administrador requeridos'
            }), HTTPStatus.FORBIDDEN
        
        # Obtener usuarios del repositorio
        # Usar el mismo repositorio que ya está configurado en auth_service
        users = auth_service.user_repository.find_all()
        
        # Obtener resumen de usuarios
        summary = auth_service.user_repository.get_users_summary()
        
        # Filtrar información sensible de los usuarios
        safe_users = []
        for user_data in users:
            safe_user = {
                'id': user_data.get('_id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'full_name': user_data.get('full_name'),
                'role': user_data.get('role'),
                'status': user_data.get('status'),
                'location': user_data.get('location'),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login')
            }
            safe_users.append(safe_user)
        
        current_app.logger.info(f"Lista de usuarios obtenida por admin: {user.username}")
        return jsonify({
            'success': True,
            'users': safe_users,
            'summary': summary,
            'total': len(safe_users)
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo usuarios: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@auth_bp.route('/refresh', methods=['POST'])
@auth_rate_limit()
def refresh_token():
    """
    Endpoint para renovar access token usando refresh token
    
    Body:
        refresh_token: string (refresh token)
    
    Returns:
        200: Nuevos tokens
        401: Refresh token inválido o expirado
        400: Datos inválidos
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            return jsonify({
                'success': False,
                'message': 'Refresh token requerido'
            }), HTTPStatus.BAD_REQUEST
        
        refresh_token = data.get('refresh_token')
        
        # Obtener servicio de autenticación
        auth_service = get_auth_service()
        
        # Renovar tokens
        token_response = auth_service.refresh_access_token(refresh_token)
        
        if not token_response:
            current_app.logger.warning("Intento de renovación de token fallido")
            return jsonify({
                'success': False,
                'message': 'Refresh token inválido o expirado'
            }), HTTPStatus.UNAUTHORIZED
        
        # Respuesta exitosa
        current_app.logger.info(f"Tokens renovados para usuario: {token_response.user.username}")
        return jsonify({
            'success': True,
            'message': 'Tokens renovados exitosamente',
            'access_token': token_response.access_token,
            'refresh_token': token_response.refresh_token,
            'token_type': token_response.token_type,
            'expires_in': token_response.expires_in,
            'user': {
                'id': token_response.user.id,
                'username': token_response.user.username,
                'email': token_response.user.email,
                'full_name': token_response.user.full_name,
                'role': token_response.user.role,
                'location': token_response.user.location
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error renovando tokens: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint para cerrar sesión revocando refresh token
    
    Body:
        refresh_token: string (refresh token a revocar)
    
    Returns:
        200: Logout exitoso
        400: Datos inválidos
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            return jsonify({
                'success': False,
                'message': 'Refresh token requerido'
            }), HTTPStatus.BAD_REQUEST
        
        refresh_token = data.get('refresh_token')
        
        # Obtener servicio de autenticación
        auth_service = get_auth_service()
        
        # Cerrar sesión
        success = auth_service.logout_user(refresh_token)
        
        if success:
            current_app.logger.info("Logout exitoso")
            return jsonify({
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }), HTTPStatus.OK
        else:
            current_app.logger.warning("Error en logout - refresh token no encontrado")
            return jsonify({
                'success': False,
                'message': 'Token de sesión no válido'
            }), HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        current_app.logger.error(f"Error en logout: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@auth_bp.route('/test-cors', methods=['GET', 'OPTIONS'])
def test_cors():
    """
    Endpoint de prueba para verificar configuración CORS
    
    Returns:
        200: Respuesta de prueba con headers CORS
    """
    try:
        current_app.logger.info("Endpoint de prueba CORS llamado")
        return jsonify({
            'success': True,
            'message': 'CORS configurado correctamente',
            'timestamp': '2024-01-01T00:00:00Z'
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de prueba CORS: {e}")
        return jsonify({
            'success': False,
            'message': 'Error en endpoint de prueba'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
