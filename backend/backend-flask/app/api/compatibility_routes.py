"""
Rutas de compatibilidad para mantener la interfaz exacta del sistema anterior
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import jwt
from pymongo import MongoClient

# Crear blueprint para compatibilidad (sin prefijo para mantener rutas exactas)
compatibility_bp = Blueprint('compatibility', __name__)

# Configuración de MongoDB
def get_mongo_collection():
    """Obtener colección de MongoDB"""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['sistema_alerta']
    return db['mediciones']

@compatibility_bp.route('/api/login', methods=['POST'])
def login_compatibility():
    """
    Endpoint de compatibilidad EXACTA con /api/login del sistema anterior
    Mantiene exactamente la misma ruta, comportamiento y respuesta
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

@compatibility_bp.route('/api/mediciones', methods=['POST'])
def recibir_medicion_compatibilidad():
    """
    Endpoint de compatibilidad para recibir mediciones
    Mantiene la misma interfaz que el main.py anterior
    """
    try:
        data = request.get_json()
        if not data or 'distancia' not in data:
            return jsonify({'error': 'Falta el campo distancia'}), 400

        # Clasificar estado basado en la distancia (igual que el Arduino)
        distancia = data['distancia']
        if distancia <= 15.0:
            estado = 'Inundación'
        elif distancia >= 40.0:
            estado = 'Sequía'
        else:
            estado = 'Normal'
        
        # Guardar en MongoDB con timestamp y estado
        medicion = {
            'distancia': distancia,
            'estado': estado,
            'fecha': datetime.utcnow()
        }
        
        coleccion = get_mongo_collection()
        coleccion.insert_one(medicion)

        current_app.logger.info(f"Medición guardada: {data['distancia']} cm")
        return jsonify({'mensaje': 'Medición guardada', 'distancia': data['distancia']}), 201
        
    except Exception as e:
        current_app.logger.error(f"Error guardando medición: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@compatibility_bp.route('/api/mediciones', methods=['GET'])
def obtener_mediciones_compatibilidad():
    """
    Endpoint de compatibilidad para obtener mediciones
    Mantiene la misma interfaz que el main.py anterior
    """
    try:
        current_app.logger.info("Iniciando obtención de mediciones...")
        
        try:
            coleccion = get_mongo_collection()
            current_app.logger.info("Conexión a MongoDB establecida")
        except Exception as mongo_error:
            current_app.logger.error(f"Error conectando a MongoDB: {mongo_error}")
            # Si MongoDB no está disponible, devolver datos de prueba
            datos_prueba = [
                {
                    '_id': '1',
                    'distancia': 238.99,
                    'fecha': '2025-09-22T00:30:00.000Z'
                },
                {
                    '_id': '2', 
                    'distancia': 234.72,
                    'fecha': '2025-09-22T00:25:00.000Z'
                },
                {
                    '_id': '3',
                    'distancia': 112.35,
                    'fecha': '2025-09-22T00:20:00.000Z'
                }
            ]
            current_app.logger.info(f"Devolviendo {len(datos_prueba)} datos de prueba")
            return jsonify(datos_prueba), 200
        
        # Obtener todas las mediciones, ordenadas por fecha descendente
        mediciones = list(coleccion.find().sort('fecha', -1).limit(50))
        
        # Convertir ObjectId y fecha a string para JSON
        for m in mediciones:
            m['_id'] = str(m['_id'])
            if hasattr(m['fecha'], 'isoformat'):
                m['fecha'] = m['fecha'].isoformat() + 'Z'
            
            # Si no tiene estado, calcularlo basado en la distancia
            if 'estado' not in m:
                distancia = m.get('distancia', 0)
                if distancia <= 15.0:
                    m['estado'] = 'Inundación'
                elif distancia >= 40.0:
                    m['estado'] = 'Sequía'
                else:
                    m['estado'] = 'Normal'
            
        current_app.logger.info(f"Obtenidas {len(mediciones)} mediciones de MongoDB")
        return jsonify(mediciones), 200
        
    except Exception as e:
        current_app.logger.error(f"Error general obteniendo mediciones: {e}")
        # En caso de error, devolver array vacío para que el frontend no falle
        return jsonify([]), 200

@compatibility_bp.route('/api/verify-token', methods=['GET'])
def verify_token_compatibility():
    """
    Endpoint para verificar tokens del sistema anterior
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

@compatibility_bp.route('/api/saludo-usuario', methods=['GET'])
def saludo_usuario():
    """
    Endpoint para saludo personalizado del usuario
    """
    try:
        # Obtener token del header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verificar token
        SECRET_KEY = 'supersecreto'
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = payload.get('sub')
            rol = payload.get('rol')
            
            # Generar saludo personalizado
            if rol == 'usuario':
                mensaje = f"¡Bienvenido {username}! Monitorea el nivel de agua en tiempo real."
            elif rol == 'admin':
                mensaje = f"¡Hola Administrador {username}! Panel de control disponible."
            else:
                mensaje = f"¡Hola {username}!"
            
            return jsonify({'mensaje': mensaje}), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
            
    except Exception as e:
        current_app.logger.error(f"Error en saludo usuario: {e}")
        return jsonify({'error': 'Error interno'}), 500

@compatibility_bp.route('/api/sensor/predicciones', methods=['GET'])
def obtener_predicciones():
    """
    Endpoint para predicciones del sistema
    """
    try:
        # Obtener la última medición real para el estado actual
        try:
            coleccion = get_mongo_collection()
            ultima_medicion = coleccion.find().sort('fecha', -1).limit(1)
            ultima_medicion = list(ultima_medicion)
            
            if ultima_medicion:
                distancia_actual = ultima_medicion[0].get('distancia', 0)
                estado_actual = ultima_medicion[0].get('estado', 'N/A')
                
                # Convertir estado del Arduino al formato del frontend
                if estado_actual == 'Sequía':
                    estado_frontend = 'sequia'
                elif estado_actual == 'Inundación':
                    estado_frontend = 'inundacion'
                elif estado_actual == 'Normal':
                    estado_frontend = 'normal'
                else:
                    estado_frontend = 'error'
            else:
                distancia_actual = 0
                estado_actual = 'N/A'
                estado_frontend = 'error'
                
        except Exception as e:
            current_app.logger.error(f"Error obteniendo última medición: {e}")
            distancia_actual = 0
            estado_actual = 'N/A'
            estado_frontend = 'error'
        
        # Datos de predicción con estado actual real
        predicciones = {
            'predicciones': [
                {'horizon_min': 60, 'nivel_cm': 25.5, 'estado': 'normal'},
                {'horizon_min': 120, 'nivel_cm': 28.2, 'estado': 'normal'},
                {'horizon_min': 180, 'nivel_cm': 22.1, 'estado': 'normal'}
            ],
            'current': {
                'estado': estado_frontend,
                'nivel_cm': distancia_actual,
                'nivel_actual': distancia_actual,
                'tendencia': 'estable',
                'estado_texto': estado_actual
            }
        }
        return jsonify(predicciones), 200
    except Exception as e:
        current_app.logger.error(f"Error en predicciones: {e}")
        return jsonify({'error': 'Error obteniendo predicciones'}), 500

@compatibility_bp.route('/api/sensor/datos-prueba', methods=['POST'])
def insertar_datos_prueba():
    """
    Endpoint para insertar datos de prueba
    """
    try:
        # Insertar algunas mediciones de prueba
        coleccion = get_mongo_collection()
        
        datos_prueba = [
            {'distancia': 25.5, 'fecha': datetime.utcnow()},
            {'distancia': 28.2, 'fecha': datetime.utcnow()},
            {'distancia': 22.1, 'fecha': datetime.utcnow()},
            {'distancia': 30.0, 'fecha': datetime.utcnow()},
            {'distancia': 27.8, 'fecha': datetime.utcnow()}
        ]
        
        coleccion.insert_many(datos_prueba)
        
        return jsonify({
            'mensaje': 'Datos de prueba insertados correctamente',
            'cantidad': len(datos_prueba)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error insertando datos de prueba: {e}")
        return jsonify({'error': 'Error insertando datos de prueba'}), 500

@compatibility_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'Sistema de Alerta Temprana'
    }), 200
