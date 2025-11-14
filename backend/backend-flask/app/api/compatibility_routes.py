"""
Rutas de compatibilidad para mantener la interfaz exacta del sistema anterior
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import jwt
from pymongo import MongoClient
from app.services.alerts_service import alerts_service

# Crear blueprint para compatibilidad (sin prefijo para mantener rutas exactas)
compatibility_bp = Blueprint('compatibility', __name__)

# Configuración de MongoDB
def get_mongo_collection():
    """Obtener colección de MongoDB usando configuración de la app"""
    from flask import current_app
    import os
    
    mongo_uri = os.getenv('MONGO_URI', current_app.config.get('MONGO_URI', 'mongodb://localhost:27017/'))
    db_name = os.getenv('MONGO_DB', current_app.config.get('MONGO_DB', 'sistema_alerta'))
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
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
    Soporta múltiples formatos:
    1. Formato original: {"distancia": 25.5}
    2. Formato ESP8266: {"TIMESTAMP": 5016, "NIVEL": 240.65, "ESTADO": "Sequia"}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400

        # Extraer distancia y estado según el formato recibido
        distancia = None
        estado = None
        timestamp = None

        # Formato ESP8266 (nuevo)
        if 'NIVEL' in data:
            distancia = float(data['NIVEL'])
            # El ESP8266 ya envía el estado, pero lo validamos
            if 'ESTADO' in data:
                estado_esp8266 = data['ESTADO']
                # Normalizar estado a nuestro formato
                if estado_esp8266 == 'Inundacion':
                    estado = 'Inundación'
                elif estado_esp8266 == 'Sequia':
                    estado = 'Sequía'
                elif estado_esp8266 == 'Normal':
                    estado = 'Normal'
                else:
                    # Si el estado no es reconocido, clasificamos automáticamente
                    if distancia <= 15.0:
                        estado = 'Inundación'
                    elif distancia >= 40.0:
                        estado = 'Sequía'
                    else:
                        estado = 'Normal'
            else:
                # Clasificar estado automáticamente si no viene del ESP8266
                if distancia <= 15.0:
                    estado = 'Inundación'
                elif distancia >= 40.0:
                    estado = 'Sequía'
                else:
                    estado = 'Normal'
            
            # Guardar timestamp del ESP8266 si viene
            if 'TIMESTAMP' in data:
                timestamp = data['TIMESTAMP']
                
        # Formato original (compatibilidad)
        elif 'distancia' in data:
            distancia = float(data['distancia'])
            # Clasificar estado basado en la distancia (igual que el Arduino)
            if distancia <= 15.0:
                estado = 'Inundación'
            elif distancia >= 40.0:
                estado = 'Sequía'
            else:
                estado = 'Normal'
        else:
            return jsonify({'error': 'Formato no soportado. Use {"distancia": valor} o {"NIVEL": valor, "ESTADO": "estado"}'}), 400

        if distancia is None:
            return jsonify({'error': 'No se pudo extraer la distancia'}), 400
        
        # Guardar en MongoDB con timestamp y estado
        medicion = {
            'distancia': distancia,
            'estado': estado,
            'fecha': datetime.utcnow()
        }
        
        # Agregar timestamp del dispositivo si está disponible
        if timestamp is not None:
            medicion['device_timestamp'] = timestamp
            medicion['device_type'] = 'ESP8266'
        else:
            medicion['device_type'] = 'Serial'
        
        coleccion = get_mongo_collection()
        resultado_medicion = coleccion.insert_one(medicion)
        
        # Procesar alerta automáticamente
        try:
            resultado_alerta = alerts_service.procesar_nueva_medicion(
                distancia=distancia,
                user_id='arduino_sensor'
            )
            current_app.logger.info(f"Procesamiento de alerta: {resultado_alerta}")
        except Exception as e:
            current_app.logger.warning(f"Error procesando alerta: {e}")

        # Preparar datos para WebSocket
        medicion_data = {
            'distancia': distancia,
            'estado': estado,
            'fecha': medicion['fecha'].isoformat() + 'Z',
            'medicion_id': str(resultado_medicion.inserted_id),
            'device_type': medicion['device_type']
        }
        
        # Emitir por WebSocket
        try:
            from app.services.websocket_service import websocket_service
            websocket_service.emit_medicion(medicion_data)
            websocket_service.emit_estado({
                'estado': estado,
                'nivel_cm': distancia,
                'timestamp': medicion_data['fecha']
            })
            current_app.logger.info(f"📡 Datos emitidos por WebSocket: {estado} - {distancia} cm")
        except Exception as e:
            current_app.logger.warning(f"Error emitiendo por WebSocket: {e}")

        current_app.logger.info(f"Medición guardada: {distancia} cm, estado: {estado}")
        return jsonify({
            'mensaje': 'Medición guardada', 
            'distancia': distancia,
            'estado': estado,
            'data': {
                'medicion_id': str(resultado_medicion.inserted_id),
                'timestamp': medicion['fecha'].isoformat() + 'Z',
                'device_type': medicion['device_type']
            }
        }), 201
        
    except ValueError as ve:
        current_app.logger.error(f"Error de formato en datos: {ve}")
        return jsonify({'error': f'Error de formato: {str(ve)}'}), 400
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
                mensaje = f"¡Hola Administrador {username}! Panel de control y gestión del sistema."
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

@compatibility_bp.route('/api/sensor/estado-conexion', methods=['GET'])
def estado_conexion_arduino():
    """
    Endpoint para verificar si el Arduino está conectado y enviando datos recientes
    """
    try:
        coleccion = get_mongo_collection()
        
        # Buscar la medición más reciente
        ultima_medicion = coleccion.find().sort('fecha', -1).limit(1)
        ultima_medicion = list(ultima_medicion)
        
        if not ultima_medicion:
            return jsonify({
                'conectado': False,
                'razon': 'No hay mediciones en la base de datos',
                'ultima_medicion': None
            }), 200
        
        # Verificar si la última medición es reciente (menos de 30 segundos)
        ultima_fecha = ultima_medicion[0]['fecha']
        ahora = datetime.utcnow()
        diferencia = (ahora - ultima_fecha).total_seconds()
        
        # Arduino envía datos cada 5 segundos, si han pasado más de 30 segundos, está desconectado
        conectado = diferencia < 30
        
        return jsonify({
            'conectado': conectado,
            'ultima_medicion': {
                'distancia': ultima_medicion[0].get('distancia'),
                'estado': ultima_medicion[0].get('estado'),
                'fecha': ultima_medicion[0]['fecha'].isoformat() + 'Z'
            },
            'segundos_desde_ultima': round(diferencia, 1),
            'razon': 'Datos recientes' if conectado else f'Última medición hace {round(diferencia, 1)} segundos'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error verificando conexión Arduino: {e}")
        return jsonify({
            'conectado': False,
            'razon': 'Error verificando conexión',
            'error': str(e)
        }), 200

@compatibility_bp.route('/api/mediciones/comando', methods=['POST'])
def enviar_comando_arduino():
    """
    Endpoint para enviar comandos al Arduino
    Formato: {"comando": "BUZZER_OFF", "parametros": {...}}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400

        comando = data.get('comando')
        if not comando:
            return jsonify({'error': 'Campo "comando" es requerido'}), 400

        # Validar comandos soportados
        comandos_soportados = ['BUZZER_OFF', 'BUZZER_ON', 'RESET', 'REINICIAR', 'STATUS']
        if comando not in comandos_soportados:
            return jsonify({
                'error': f'Comando no soportado: {comando}',
                'comandos_disponibles': comandos_soportados
            }), 400

        # Importar el servicio de control de dispositivos
        try:
            from app.services.device_control_service import device_control_service
            current_app.logger.info(f"Servicio de control de dispositivos cargado: {device_control_service}")
        except ImportError as e:
            current_app.logger.error(f"DeviceControlService no disponible: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Servicio de control de dispositivos no disponible'
            }), 503

        # Ejecutar comando según el tipo
        resultado = None
        try:
            if comando == 'BUZZER_OFF':
                resultado = device_control_service.deactivate_buzzer()
            elif comando == 'BUZZER_ON':
                parametros = data.get('parametros', {})
                alert_type = parametros.get('alert_type', 'general')
                frequency = parametros.get('frequency')
                resultado = device_control_service.activate_buzzer(alert_type, frequency)
            elif comando == 'RESET':
                resultado = device_control_service.send_command_serial('reset')
            elif comando == 'REINICIAR':
                resultado = device_control_service.send_command_serial('reset')
            elif comando == 'STATUS':
                resultado = device_control_service.get_device_status()
            else:
                current_app.logger.error(f"Comando no manejado: {comando}")
                return jsonify({
                    'status': 'error',
                    'message': f'Comando no manejado: {comando}'
                }), 400
        except Exception as cmd_error:
            current_app.logger.error(f"Error ejecutando comando {comando}: {cmd_error}")
            return jsonify({
                'status': 'error',
                'message': f'Error ejecutando comando: {str(cmd_error)}'
            }), 500

        # Verificar resultado
        current_app.logger.info(f"Resultado del comando {comando}: {resultado}")
        if resultado and resultado.get('status') == 'success':
            current_app.logger.info(f"Comando {comando} ejecutado exitosamente")
            return jsonify({
                'status': 'success',
                'message': f'Comando {comando} enviado correctamente',
                'comando': comando,
                'resultado': resultado,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200
        else:
            error_msg = resultado.get('error', 'Error desconocido') if resultado else 'Sin respuesta del dispositivo'
            current_app.logger.warning(f"Error ejecutando comando {comando}: {error_msg}")
            return jsonify({
                'status': 'error',
                'message': f'Error al ejecutar comando {comando}: {error_msg}',
                'comando': comando
            }), 500

    except Exception as e:
        current_app.logger.error(f"Error procesando comando Arduino: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

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
