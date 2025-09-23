"""
Rutas para operaciones geoespaciales del Sistema de Alerta Temprana
Endpoints para consultas de alertas por proximidad geográfica
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime
from app.services.geospatial_service import geospatial_service

# Crear blueprint para operaciones geoespaciales
geospatial_bp = Blueprint('geospatial', __name__, url_prefix='/api')

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
            SECRET_KEY = 'supersecreto'  # Mismo secret que otros endpoints
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

@geospatial_bp.route('/alertas', methods=['GET'])
@token_required
def obtener_alertas_georreferenciadas(current_user):
    """
    Obtener alertas dentro de un área circular específica
    
    Query params:
    - lat: Latitud del punto central (requerido)
    - lng: Longitud del punto central (requerido)
    - radio: Radio en metros (opcional, default: 5000)
    
    Returns:
    - Lista de alertas dentro del radio especificado
    """
    try:
        # Obtener parámetros de consulta
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radio = request.args.get('radio', type=int, default=5000)
        
        # Validar parámetros requeridos
        if lat is None or lng is None:
            return jsonify({
                'error': 'Parámetros lat y lng son requeridos',
                'ejemplo': '/api/alertas?lat=-34.6037&lng=-58.3816&radio=5000'
            }), 400
        
        # Validar rango de coordenadas
        if not (-90 <= lat <= 90):
            return jsonify({
                'error': 'Latitud debe estar entre -90 y 90'
            }), 400
        
        if not (-180 <= lng <= 180):
            return jsonify({
                'error': 'Longitud debe estar entre -180 y 180'
            }), 400
        
        # Validar radio
        if radio <= 0 or radio > 100000:  # Máximo 100km
            return jsonify({
                'error': 'Radio debe estar entre 1 y 100000 metros'
            }), 400
        
        # Obtener alertas usando el servicio geoespacial
        resultado = geospatial_service.get_alerts_in_radius(lat, lng, radio)
        
        if not resultado['success']:
            return jsonify({
                'error': 'Error obteniendo alertas geoespaciales',
                'details': resultado['error']
            }), 500
        
        # Log de la consulta
        current_app.logger.info(
            f"Consulta geoespacial - user={current_user['username']}, "
            f"lat={lat}, lng={lng}, radio={radio}m, alertas={resultado['total']}"
        )
        
        return jsonify({
            'success': True,
            'alerts': resultado['alerts'],
            'total': resultado['total'],
            'center': resultado['center'],
            'radius_meters': resultado['radius_meters'],
            'timestamp': resultado['timestamp'],
            'consultado_por': current_user['username']
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Parámetros inválidos',
            'details': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error en consulta geoespacial: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@geospatial_bp.route('/sensores', methods=['GET'])
@token_required
def obtener_sensores(current_user):
    """
    Obtener todos los sensores registrados con sus ubicaciones
    
    Returns:
    - Lista de sensores con coordenadas geográficas
    """
    try:
        resultado = geospatial_service.get_all_sensors()
        
        if not resultado['success']:
            return jsonify({
                'error': 'Error obteniendo sensores',
                'details': resultado['error']
            }), 500
        
        current_app.logger.info(
            f"Consulta de sensores - user={current_user['username']}, "
            f"total={resultado['total']}"
        )
        
        return jsonify({
            'success': True,
            'sensors': resultado['sensors'],
            'total': resultado['total'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'consultado_por': current_user['username']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo sensores: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@geospatial_bp.route('/sensores', methods=['POST'])
@token_required
def crear_sensor(current_user):
    """
    Crear o actualizar un sensor con ubicación geográfica
    
    Body params:
    - sensor_id: ID único del sensor (requerido)
    - lat: Latitud (requerido)
    - lng: Longitud (requerido)
    - nombre: Nombre descriptivo (opcional)
    - descripcion: Descripción del sensor (opcional)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        # Validar parámetros requeridos
        sensor_id = data.get('sensor_id')
        lat = data.get('lat')
        lng = data.get('lng')
        
        if not sensor_id:
            return jsonify({'error': 'sensor_id es requerido'}), 400
        
        if lat is None or lng is None:
            return jsonify({'error': 'lat y lng son requeridos'}), 400
        
        # Validar coordenadas
        if not (-90 <= lat <= 90):
            return jsonify({'error': 'Latitud debe estar entre -90 y 90'}), 400
        
        if not (-180 <= lng <= 180):
            return jsonify({'error': 'Longitud debe estar entre -180 y 180'}), 400
        
        # Crear sensor usando el servicio geoespacial
        resultado = geospatial_service.create_sensor_with_location(
            sensor_id=sensor_id,
            lat=lat,
            lng=lng,
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion')
        )
        
        if not resultado['success']:
            return jsonify({
                'error': 'Error creando sensor',
                'details': resultado['error']
            }), 500
        
        current_app.logger.info(
            f"Sensor creado/actualizado - user={current_user['username']}, "
            f"sensor_id={sensor_id}, lat={lat}, lng={lng}"
        )
        
        return jsonify({
            'success': True,
            'mensaje': f"Sensor {sensor_id} {'creado' if resultado['operation'] == 'created' else 'actualizado'} exitosamente",
            'sensor_id': resultado['sensor_id'],
            'location': resultado['location'],
            'operation': resultado['operation'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'creado_por': current_user['username']
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creando sensor: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@geospatial_bp.route('/mediciones', methods=['POST'])
@token_required
def guardar_medicion_georreferenciada(current_user):
    """
    Guardar medición con datos geoespaciales
    
    Body params:
    - sensor_id: ID del sensor (requerido)
    - nivel: Nivel de agua en cm (requerido)
    - estado: Estado (sequia, normal, inundacion) (requerido)
    - lat: Latitud (opcional, se obtiene del sensor si no se proporciona)
    - lng: Longitud (opcional, se obtiene del sensor si no se proporciona)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        # Validar parámetros requeridos
        sensor_id = data.get('sensor_id')
        nivel = data.get('nivel')
        estado = data.get('estado')
        
        if not sensor_id:
            return jsonify({'error': 'sensor_id es requerido'}), 400
        
        if nivel is None:
            return jsonify({'error': 'nivel es requerido'}), 400
        
        if not estado:
            return jsonify({'error': 'estado es requerido'}), 400
        
        # Validar estado
        if estado not in ['sequia', 'normal', 'inundacion']:
            return jsonify({
                'error': 'estado debe ser: sequia, normal, o inundacion'
            }), 400
        
        # Validar nivel
        try:
            nivel = float(nivel)
            if nivel < 0:
                return jsonify({'error': 'nivel debe ser mayor o igual a 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'nivel debe ser un número válido'}), 400
        
        # Guardar medición usando el servicio geoespacial
        resultado = geospatial_service.save_measurement_with_location(
            sensor_id=sensor_id,
            nivel=nivel,
            estado=estado,
            lat=data.get('lat'),
            lng=data.get('lng')
        )
        
        if not resultado['success']:
            return jsonify({
                'error': 'Error guardando medición',
                'details': resultado['error']
            }), 500
        
        current_app.logger.info(
            f"Medición guardada - user={current_user['username']}, "
            f"sensor_id={sensor_id}, nivel={nivel}cm, estado={estado}"
        )
        
        return jsonify({
            'success': True,
            'mensaje': 'Medición guardada exitosamente',
            'medicion_id': resultado['medicion_id'],
            'sensor_id': resultado['sensor_id'],
            'location': resultado['location'],
            'nivel': resultado['nivel'],
            'estado': resultado['estado'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'guardado_por': current_user['username']
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error guardando medición: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@geospatial_bp.route('/geospatial/health', methods=['GET'])
def health_check_geospatial():
    """
    Health check específico para el servicio geoespacial
    """
    try:
        # Verificar conexión a MongoDB
        sensors_result = geospatial_service.get_all_sensors()
        
        return jsonify({
            'status': 'healthy',
            'service': 'geospatial_service',
            'database': 'connected',
            'sensors_count': sensors_result.get('total', 0),
            'indexes': '2dsphere indexes created',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Health check geoespacial fallido: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'geospatial_service',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500
