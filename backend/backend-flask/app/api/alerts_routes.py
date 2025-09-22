"""
Rutas de API para gestión de alertas del Sistema de Alerta Temprana
Endpoints protegidos con JWT para administración de alertas
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime
from app.services.alerts_service import alerts_service

# Crear blueprint para alertas
alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/v1')

def token_required(f):
    """Decorador para requerir token JWT válido"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token de autorización requerido'}), 401
        
        try:
            SECRET_KEY = 'supersecreto'  # Mismo secret que compatibility_routes
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = {
                'username': data['sub'],
                'rol': data['rol']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('rol') != 'admin':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@alerts_bp.route('/alertas', methods=['GET'])
@token_required
def obtener_alertas(current_user):
    """
    Obtener alertas del sistema
    Query params:
    - activas: true/false (filtrar solo alertas activas)
    - limite: número máximo de alertas (default: 50)
    """
    try:
        # Obtener parámetros de consulta
        solo_activas = request.args.get('activas', 'false').lower() == 'true'
        limite = int(request.args.get('limite', 50))
        
        if solo_activas:
            alertas = alerts_service.obtener_alertas_activas()
        else:
            alertas = alerts_service.obtener_historial_alertas(limite)
        
        current_app.logger.info(
            f"Consulta de alertas - user={current_user['username']}, "
            f"activas={solo_activas}, total={len(alertas)}"
        )
        
        return jsonify({
            'alertas': alertas,
            'total': len(alertas),
            'filtros': {
                'solo_activas': solo_activas,
                'limite': limite
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo alertas: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@alerts_bp.route('/alertas/estado', methods=['GET'])
@token_required
def obtener_estado_sistema(current_user):
    """
    Obtener el estado actual del sistema de alertas
    """
    try:
        estado = alerts_service.obtener_estado_sistema()
        
        current_app.logger.info(
            f"Consulta de estado del sistema - user={current_user['username']}, "
            f"estado={estado['estado_actual']}"
        )
        
        return jsonify(estado), 200
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estado del sistema: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@alerts_bp.route('/alertas/<string:alerta_id>/desactivar', methods=['PATCH'])
@token_required
@admin_required
def desactivar_alerta(current_user, alerta_id):
    """
    Desactivar una alerta específica (solo administradores)
    """
    try:
        # Obtener motivo opcional del body
        data = request.get_json() or {}
        motivo = data.get('motivo', 'desactivacion_manual_admin')
        
        # Validar ID de alerta
        if not alerta_id or len(alerta_id) != 24:
            return jsonify({
                'error': 'ID de alerta inválido'
            }), 400
        
        # Desactivar alerta
        resultado = alerts_service.desactivar_alerta(
            alerta_id=alerta_id,
            user_id=current_user['username'],
            motivo=motivo
        )
        
        if resultado['success']:
            current_app.logger.info(
                f"Alerta desactivada - id={alerta_id}, "
                f"admin={current_user['username']}, motivo={motivo}"
            )
            
            return jsonify({
                'mensaje': 'Alerta desactivada exitosamente',
                'alerta_id': alerta_id,
                'desactivada_por': current_user['username'],
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                **resultado
            }), 200
        else:
            return jsonify({
                'error': resultado.get('error', 'No se pudo desactivar la alerta')
            }), 400
            
    except ValueError as e:
        return jsonify({
            'error': 'ID de alerta inválido',
            'details': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error desactivando alerta {alerta_id}: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@alerts_bp.route('/alertas/buzzer/desactivar', methods=['POST'])
@token_required
@admin_required
def desactivar_buzzer_manual(current_user):
    """
    Desactivar manualmente el buzzer de todas las alertas activas
    """
    try:
        # Obtener todas las alertas activas y desactivar sus buzzers
        alertas_activas = alerts_service.obtener_alertas_activas()
        
        if not alertas_activas:
            return jsonify({
                'mensaje': 'No hay alertas activas con buzzer',
                'alertas_afectadas': 0
            }), 200
        
        alertas_desactivadas = []
        
        for alerta in alertas_activas:
            if alerta.get('buzzer_activo', False):
                resultado = alerts_service.desactivar_alerta(
                    alerta_id=alerta['_id'],
                    user_id=current_user['username'],
                    motivo='buzzer_desactivado_manual'
                )
                if resultado['success']:
                    alertas_desactivadas.append(alerta['_id'])
        
        current_app.logger.info(
            f"Buzzer desactivado manualmente - admin={current_user['username']}, "
            f"alertas_afectadas={len(alertas_desactivadas)}"
        )
        
        return jsonify({
            'mensaje': 'Buzzer desactivado exitosamente',
            'alertas_afectadas': len(alertas_desactivadas),
            'alertas_desactivadas': alertas_desactivadas,
            'desactivado_por': current_user['username'],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error desactivando buzzer manualmente: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@alerts_bp.route('/alertas/configuracion', methods=['GET'])
@token_required
@admin_required
def obtener_configuracion_alertas(current_user):
    """
    Obtener configuración actual de umbrales de alerta
    """
    try:
        configuracion = {
            'umbrales': {
                'inundacion': alerts_service.umbral_inundacion,
                'sequia': alerts_service.umbral_sequia
            },
            'estados': {
                'inundacion': f'Nivel ≤ {alerts_service.umbral_inundacion} cm',
                'normal': f'{alerts_service.umbral_inundacion} cm < Nivel < {alerts_service.umbral_sequia} cm',
                'sequia': f'Nivel ≥ {alerts_service.umbral_sequia} cm'
            },
            'configurado_por': 'variables_entorno',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return jsonify(configuracion), 200
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo configuración: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@alerts_bp.route('/alertas/estadisticas', methods=['GET'])
@token_required
def obtener_estadisticas_alertas(current_user):
    """
    Obtener estadísticas de alertas (disponible para usuarios y admins)
    """
    try:
        # Obtener historial reciente para estadísticas
        historial = alerts_service.obtener_historial_alertas(limite=100)
        
        # Calcular estadísticas
        total_alertas = len(historial)
        alertas_activas = len([a for a in historial if a.get('alerta_activa', False)])
        
        # Contar por tipo
        tipos = {}
        for alerta in historial:
            tipo = alerta.get('tipo_alerta', 'unknown')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        # Alertas recientes (últimas 24 horas)
        ahora = datetime.utcnow()
        alertas_recientes = 0
        for alerta in historial:
            try:
                timestamp_str = alerta.get('timestamp', '').replace('Z', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if (ahora - timestamp).total_seconds() < 86400:  # 24 horas
                        alertas_recientes += 1
            except:
                continue
        
        estadisticas = {
            'resumen': {
                'total_alertas': total_alertas,
                'alertas_activas': alertas_activas,
                'alertas_recientes_24h': alertas_recientes
            },
            'por_tipo': tipos,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'consultado_por': current_user['username']
        }
        
        current_app.logger.info(
            f"Estadísticas consultadas - user={current_user['username']}, "
            f"total={total_alertas}, activas={alertas_activas}"
        )
        
        return jsonify(estadisticas), 200
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@alerts_bp.route('/dispositivos/test', methods=['POST'])
@token_required
@admin_required
def test_dispositivo(current_user):
    """
    Probar conexión y funcionalidad del dispositivo IoT
    """
    try:
        from app.services.device_control_service import device_control_service
        
        # Obtener tipo de prueba
        data = request.get_json() or {}
        test_type = data.get('test_type', 'connection')
        
        if test_type == 'connection':
            # Probar conexión
            resultado = device_control_service.test_connection()
        elif test_type == 'buzzer_on':
            # Probar activación de buzzer
            resultado = device_control_service.activate_buzzer('general', 1000)
        elif test_type == 'buzzer_off':
            # Probar desactivación de buzzer
            resultado = device_control_service.deactivate_buzzer()
        elif test_type == 'status':
            # Obtener estado del dispositivo
            resultado = device_control_service.get_device_status()
        else:
            return jsonify({
                'error': 'Tipo de prueba no válido',
                'tipos_disponibles': ['connection', 'buzzer_on', 'buzzer_off', 'status']
            }), 400
        
        current_app.logger.info(
            f"Prueba de dispositivo - admin={current_user['username']}, "
            f"tipo={test_type}, resultado={resultado.get('status', 'unknown')}"
        )
        
        return jsonify({
            'test_type': test_type,
            'resultado': resultado,
            'ejecutado_por': current_user['username'],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error en prueba de dispositivo: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@alerts_bp.route('/alertas/health', methods=['GET'])
def health_check_alertas():
    """
    Health check específico para el sistema de alertas
    """
    try:
        # Verificar conexión a base de datos
        estado_sistema = alerts_service.obtener_estado_sistema()
        
        # Verificar conexión con dispositivo
        try:
            from app.services.device_control_service import device_control_service
            device_status = device_control_service.test_connection()
        except Exception as e:
            device_status = {'error': str(e)}
        
        return jsonify({
            'status': 'healthy',
            'service': 'alerts_system',
            'database': 'connected',
            'device_connection': device_status,
            'nivel_actual': estado_sistema.get('nivel_actual', 0),
            'alertas_activas': estado_sistema.get('alertas_activas', 0),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Health check fallido: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'alerts_system',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500
