"""
Rutas para gestión de dispositivos Arduino
"""
from flask import Blueprint, request, jsonify, current_app
from http import HTTPStatus
from pymongo import MongoClient
import os

from app.models.device import DeviceCreate, DeviceUpdate
from app.services.device_scanner import DeviceScanner
from app.repositories.device_repository import DeviceRepository

# Crear blueprint
device_bp = Blueprint('devices', __name__)

def get_device_scanner():
    """Obtener instancia del escáner de dispositivos"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB', 'sensor_database')
    
    client = MongoClient(mongo_uri)
    device_repository = DeviceRepository(client, db_name)
    return DeviceScanner(device_repository)

def get_auth_service():
    """Obtener instancia del servicio de autenticación para verificar roles"""
    from app.services.auth_service import AuthService
    from app.repositories.user_repository import UserRepository
    
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB', 'sensor_database')
    
    client = MongoClient(mongo_uri)
    user_repository = UserRepository(client, db_name)
    return AuthService(user_repository)

def require_auth():
    """Decorator para requerir autenticación"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, jsonify({
            'success': False,
            'message': 'Token de autorización requerido'
        }), HTTPStatus.UNAUTHORIZED
    
    token = auth_header.split(' ')[1]
    auth_service = get_auth_service()
    user = auth_service.get_current_user(token)
    
    if not user:
        return None, jsonify({
            'success': False,
            'message': 'Token inválido o expirado'
        }), HTTPStatus.UNAUTHORIZED
    
    return user, None, None

def require_admin():
    """Decorator para requerir rol de administrador"""
    user, error_response, status_code = require_auth()
    if error_response:
        return None, error_response, status_code
    
    if user.role != 'admin':
        return None, jsonify({
            'success': False,
            'message': 'Permisos de administrador requeridos'
        }), HTTPStatus.FORBIDDEN
    
    return user, None, None

@device_bp.route('/devices/status', methods=['GET'])
def get_devices_status():
    """
    Obtiene el estado actual de todos los dispositivos.
    Acceso: admin y operador
    """
    try:
        # Verificar autenticación
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        # Verificar que sea admin u operador
        if user.role not in ['admin', 'operator']:
            return jsonify({
                'success': False,
                'message': 'Permisos insuficientes'
            }), HTTPStatus.FORBIDDEN
        
        # Obtener estado de dispositivos
        device_scanner = get_device_scanner()
        devices = device_scanner.get_device_status()
        stats = device_scanner.get_device_statistics()
        
        return jsonify({
            'success': True,
            'devices': devices,
            'statistics': stats,
            'total': len(devices)
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estado de dispositivos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@device_bp.route('/devices', methods=['GET'])
def get_all_devices():
    """
    Lista todos los dispositivos registrados.
    Acceso: solo admin
    """
    try:
        # Verificar autenticación y permisos de admin
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Obtener dispositivos
        device_scanner = get_device_scanner()
        devices = device_scanner.get_device_status()
        stats = device_scanner.get_device_statistics()
        
        return jsonify({
            'success': True,
            'devices': devices,
            'statistics': stats,
            'total': len(devices)
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error listando dispositivos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@device_bp.route('/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """
    Actualiza la información de un dispositivo.
    Acceso: solo admin
    """
    try:
        # Verificar autenticación y permisos de admin
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar campos
        name = data.get('name')
        config = data.get('config')
        
        if not name and not config:
            return jsonify({
                'success': False,
                'message': 'Se requiere al menos un campo para actualizar (name o config)'
            }), HTTPStatus.BAD_REQUEST
        
        # Actualizar dispositivo
        device_scanner = get_device_scanner()
        device = device_scanner.update_device(device_id, name, config)
        
        if not device:
            return jsonify({
                'success': False,
                'message': 'Dispositivo no encontrado'
            }), HTTPStatus.NOT_FOUND
        
        return jsonify({
            'success': True,
            'device': device.dict(),
            'message': 'Dispositivo actualizado correctamente'
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error actualizando dispositivo {device_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@device_bp.route('/devices/scan', methods=['POST'])
def scan_devices():
    """
    Fuerza un escaneo manual de dispositivos.
    Acceso: solo admin
    """
    try:
        # Verificar autenticación y permisos de admin
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Ejecutar escaneo
        device_scanner = get_device_scanner()
        stats = device_scanner.scan_devices()
        
        if 'error' in stats:
            return jsonify({
                'success': False,
                'message': f'Error durante el escaneo: {stats["error"]}'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        return jsonify({
            'success': True,
            'scan_stats': stats,
            'message': 'Escaneo completado'
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error durante escaneo manual: {e}")
        return jsonify({
            'success': False,
            'message': 'Error durante el escaneo'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@device_bp.route('/devices/<device_id>/status', methods=['PUT'])
def update_device_status(device_id):
    """
    Actualiza manualmente el estado de un dispositivo.
    Acceso: solo admin
    """
    try:
        # Verificar autenticación y permisos de admin
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # Validar datos de entrada
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'message': 'Campo status requerido'
            }), HTTPStatus.BAD_REQUEST
        
        status = data.get('status')
        if status not in ['ACTIVE', 'INACTIVE']:
            return jsonify({
                'success': False,
                'message': 'Status debe ser ACTIVE o INACTIVE'
            }), HTTPStatus.BAD_REQUEST
        
        # Actualizar estado
        device_scanner = get_device_scanner()
        device_repository = device_scanner.device_repository
        
        from app.models.device import DeviceStatus
        success = device_repository.update_status(device_id, DeviceStatus(status))
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Dispositivo no encontrado'
            }), HTTPStatus.NOT_FOUND
        
        # Obtener dispositivo actualizado
        device = device_repository.find_by_id(device_id)
        
        return jsonify({
            'success': True,
            'device': device.dict() if device else None,
            'message': f'Estado actualizado a {status}'
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error actualizando estado del dispositivo {device_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
