"""
Rutas de la API para sensores
"""
from flask import Blueprint, request, jsonify
from app.utils.decorators import validate_json, handle_exceptions
from app.models.sensor_model import EstadoSensorStats
from app.factory import service_factory

# Crear el blueprint para las rutas del sensor
sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/sensor/lectura', methods=['POST'])
@validate_json
@handle_exceptions
def procesar_lectura():
    """
    Procesa una nueva lectura del sensor
    
    Request Body:
    {
        "nivel_agua": 10.5
    }
    
    Returns:
    200: {
        "mensaje": "Lectura procesada exitosamente",
        "data": {
            "_id": "ObjectId",
            "nivel_agua": 10.5,
            "estado": "normal",
            "timestamp": "2025-05-16 14:48:17"
        }
    }
    400: {"error": "Mensaje de error"}
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.proceso_leer_sensor()
    return jsonify(response), status_code

@sensor_bp.route('/sensor/lecturas', methods=['POST'])
@validate_json
@handle_exceptions
def procesar_lecturas():
    """
    Procesa una lista de lecturas del sensor
    
    Request Body:
    [
        {
            "raw_data": "nivel_agua: 10.5cm"
        }
    ]
    
    Returns:
    200: {
        "mensaje": "Lecturas procesadas exitosamente",
        "data": [...]
    }
    400: {"error": "Mensaje de error"}
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.proceso_lecturas()
    return jsonify(response), status_code

@sensor_bp.route('/sensor/todas-lecturas', methods=['GET'])
@handle_exceptions
def todas_lecturas():
    """
    Obtiene todas las lecturas del sensor
    
    Returns:
    200: Lista de lecturas
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.get_todas_lecturas()
    return jsonify(response), status_code

@sensor_bp.route("/sensor/rango-tiempo/<rango>", methods=['GET'])
@handle_exceptions
def rango_tiempo(rango):
    """
    Obtiene las lecturas del sensor en un rango de tiempo
    
    Args:
        rango: Rango de tiempo ('1h', '24h', '7d')

    Returns:
    200: Lista de lecturas en el rango especificado
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.get_lecturas_rango(rango)
    return jsonify(response), status_code

@sensor_bp.route("/sensor/estadisticas-diarias", methods=['GET'])
@handle_exceptions
def estadisticas_diarias():
    """
    Obtiene estadísticas diarias del nivel de agua
    
    Returns:
    200: Estadísticas diarias
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.get_estadisticas_diarias()
    return jsonify(response), status_code

@sensor_bp.route("/sensor/ultima-lectura", methods=['GET'])
@handle_exceptions
def ultima_lectura():
    """
    Obtiene la última lectura del sensor
    
    Returns:
    200: Última lectura
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.get_ultima_lectura()
    return jsonify(response), status_code

@sensor_bp.route("/sensor/predicciones", methods=['GET'])
@handle_exceptions
def predicciones():
    """
    Obtiene predicciones de nivel de agua
    
    Returns:
    200: Lista de predicciones
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.get_predicciones()
    return jsonify(response), status_code

@sensor_bp.route('/sensor/estadisticas-estados', methods=['GET'])
@handle_exceptions
def obtener_estadisticas_estados():
    """
    Obtener estadísticas de estados del sensor (sequía, normal, inundación)
    
    Returns:
    200: Estadísticas de estados
    500: {"error": "Error interno del servidor"}
    """
    try:
        resultado = service_factory.sensor_controller.obtener_estadisticas_estados()
        if isinstance(resultado, tuple):
            data, status_code = resultado
            # Si data es un objeto EstadoSensorStats, usamos dict(), si es un dict, lo devolvemos directamente
            if isinstance(data, EstadoSensorStats):
                return jsonify(data.dict()), status_code
            else:
                return jsonify(data), status_code
        else:
            if isinstance(resultado, EstadoSensorStats):
                return jsonify(resultado.dict()), 200
            else:
                return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sensor_bp.route('/sensor/alertas', methods=['GET'])
@handle_exceptions
def obtener_alertas():
    """
    Obtiene alertas recientes (lecturas en estado de sequía o inundación)
    
    Query Parameters:
        limit: Número máximo de alertas a obtener (default: 10)
    
    Returns:
    200: Lista de alertas
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.get_alertas()
    return jsonify(response), status_code

@sensor_bp.route('/sensor/estado', methods=['GET'])
@handle_exceptions
def obtener_estado_sistema():
    """
    Obtiene el estado general del sistema
    
    Returns:
    200: Estado del sistema
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.get_estado_sistema()
    return jsonify(response), status_code
    
@sensor_bp.route('/sensor/verify-blockchain', methods=['GET'])
@handle_exceptions
def verify_blockchain():
    """
    Verifica la integridad de la cadena de bloques
    
    Returns:
    200: {"valid": true, "message": "La cadena de bloques es válida"}
    400: {"valid": false, "message": "La cadena de bloques ha sido comprometida"}
    500: {"error": "Error interno del servidor"}
    """
    response, status_code = service_factory.sensor_controller.verify_blockchain()
    return jsonify(response), status_code

# Endpoint de health check
@sensor_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
    200: {"status": "healthy", "timestamp": "..."}
    """
    response, status_code = service_factory.sensor_controller.health_check()
    return jsonify(response), status_code

# Endpoint para insertar datos de prueba (solo para desarrollo)
@sensor_bp.route('/sensor/datos-prueba', methods=['POST'])
@handle_exceptions
def insertar_datos_prueba():
    """
    Insertar datos de prueba en la base de datos
    Solo disponible en modo desarrollo
    
    Returns:
    200: {"mensaje": "Datos de prueba insertados", "total": N}
    500: {"error": "Error interno del servidor"}
    """
    from flask import current_app
    
    # Solo permitir en modo desarrollo
    if not current_app.config.get('DEBUG', False):
        return jsonify({"error": "Endpoint solo disponible en modo desarrollo"}), 403
    
    response, status_code = service_factory.sensor_controller.insertar_datos_prueba()
    return jsonify(response), status_code