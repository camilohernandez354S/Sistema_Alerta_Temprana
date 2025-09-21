"""
Rutas para recuperación de contraseñas
"""
from flask import Blueprint, request, jsonify, current_app
from http import HTTPStatus
from pymongo import MongoClient
import os

from app.models.password_reset_model import (
    PasswordResetRequest, PasswordResetConfirm, PasswordResetStats
)
from app.services.password_reset_service import PasswordResetService
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.user_repository import UserRepository
from app.utils.rate_limiter import auth_rate_limit

# Crear blueprint
password_reset_bp = Blueprint('password_reset', __name__)

def get_password_reset_service():
    """Obtener instancia del servicio de recuperación de contraseñas"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB', 'sensor_database')
    
    client = MongoClient(mongo_uri)
    reset_repository = PasswordResetRepository(client, db_name)
    user_repository = UserRepository(client, db_name)
    
    return PasswordResetService(reset_repository, user_repository)

@password_reset_bp.route('/request-reset', methods=['POST'])
@auth_rate_limit()
def request_password_reset():
    """
    Solicitar reset de contraseña
    
    Body:
        email: string (email del usuario)
    
    Returns:
        200: Solicitud procesada
        400: Datos inválidos
        429: Rate limit excedido
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        email = data.get('email')
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email es requerido'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar formato de email
        try:
            request_data = PasswordResetRequest(email=email)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Email inválido: {str(e)}'
            }), HTTPStatus.BAD_REQUEST
        
        # Procesar solicitud
        reset_service = get_password_reset_service()
        result = reset_service.request_password_reset(request_data)
        
        if result['success']:
            return jsonify(result), HTTPStatus.OK
        else:
            status_code = HTTPStatus.BAD_REQUEST
            if result.get('error_code') == 'RATE_LIMITED':
                status_code = HTTPStatus.TOO_MANY_REQUESTS
            
            return jsonify(result), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error en solicitud de reset: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@password_reset_bp.route('/validate-token', methods=['POST'])
def validate_reset_token():
    """
    Validar token de reset
    
    Body:
        token: string (token de reset)
    
    Returns:
        200: Token válido
        400: Token inválido
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        token = data.get('token')
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token es requerido'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar token
        reset_service = get_password_reset_service()
        result = reset_service.validate_reset_token(token)
        
        if result['success']:
            return jsonify(result), HTTPStatus.OK
        else:
            return jsonify(result), HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        current_app.logger.error(f"Error validando token: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@password_reset_bp.route('/confirm-reset', methods=['POST'])
@auth_rate_limit()
def confirm_password_reset():
    """
    Confirmar reset de contraseña
    
    Body:
        token: string (token de reset)
        new_password: string (nueva contraseña)
        confirm_password: string (confirmación de contraseña)
    
    Returns:
        200: Contraseña actualizada
        400: Datos inválidos o token inválido
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not all([token, new_password, confirm_password]):
            return jsonify({
                'success': False,
                'message': 'Token, nueva contraseña y confirmación son requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar datos
        try:
            confirm_data = PasswordResetConfirm(
                token=token,
                new_password=new_password,
                confirm_password=confirm_password
            )
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Datos inválidos: {str(e)}'
            }), HTTPStatus.BAD_REQUEST
        
        # Procesar confirmación
        reset_service = get_password_reset_service()
        result = reset_service.confirm_password_reset(confirm_data)
        
        if result['success']:
            return jsonify(result), HTTPStatus.OK
        else:
            return jsonify(result), HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        current_app.logger.error(f"Error confirmando reset: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@password_reset_bp.route('/stats', methods=['GET'])
def get_reset_stats():
    """
    Obtener estadísticas de reset (solo admin)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Estadísticas de reset
        401: No autorizado
        403: Sin permisos de admin
    """
    try:
        # Verificar autenticación (simplificado para este ejemplo)
        # En producción, usar decorador de autenticación apropiado
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Token de autorización requerido'
            }), HTTPStatus.UNAUTHORIZED
        
        # Obtener estadísticas
        reset_service = get_password_reset_service()
        stats = reset_service.get_reset_stats()
        
        return jsonify({
            'success': True,
            'stats': stats.dict()
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@password_reset_bp.route('/cleanup', methods=['POST'])
def cleanup_expired_tokens():
    """
    Limpiar tokens expirados (solo admin)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Tokens limpiados
        401: No autorizado
        403: Sin permisos de admin
    """
    try:
        # Verificar autenticación (simplificado para este ejemplo)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Token de autorización requerido'
            }), HTTPStatus.UNAUTHORIZED
        
        # Limpiar tokens expirados
        reset_service = get_password_reset_service()
        cleaned_count = reset_service.cleanup_expired_tokens()
        
        return jsonify({
            'success': True,
            'message': f'Se limpiaron {cleaned_count} tokens expirados',
            'cleaned_count': cleaned_count
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error limpiando tokens: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
