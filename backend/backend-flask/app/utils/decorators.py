"""
Decoradores útiles para la aplicación
"""
from functools import wraps
from flask import request, jsonify, current_app
import traceback

def validate_json(f):
    """
    Decorador para validar que la request contenga JSON válido
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            current_app.logger.warning("Request sin Content-Type: application/json")
            return jsonify({
                "error": "Content-Type debe ser application/json"
            }), 400
        
        try:
            # Intentar acceder al JSON para validar que sea válido
            data = request.get_json()
            if data is None:
                return jsonify({
                    "error": "JSON inválido o vacío"
                }), 400
        except Exception as e:
            current_app.logger.warning(f"JSON inválido: {e}")
            return jsonify({
                "error": "JSON mal formado"
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function

def handle_exceptions(f):
    """
    Decorador para manejo consistente de excepciones
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            current_app.logger.warning(f"ValueError en {f.__name__}: {e}")
            return jsonify({
                "error": "Error de validación",
                "message": str(e)
            }), 400
        except Exception as e:
            current_app.logger.error(f"Error en {f.__name__}: {e}")
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                "error": "Error interno del servidor",
                "message": "Ha ocurrido un error inesperado"
            }), 500
    
    return decorated_function

def validate_query_params(*required_params):
    """
    Decorador para validar parámetros de query string
    
    Args:
        *required_params: Lista de parámetros requeridos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing_params = []
            for param in required_params:
                if param not in request.args:
                    missing_params.append(param)
            
            if missing_params:
                return jsonify({
                    "error": "Parámetros faltantes",
                    "missing_params": missing_params
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit(max_requests=100, window_seconds=3600):
    """
    Decorador básico de rate limiting (requiere Redis en producción)
    Por ahora es solo un placeholder para mostrar la estructura
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # En una implementación real, aquí verificaríamos el rate limit
            # usando Redis o similar
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_api_key(f):
    """
    Decorador para requerir API key (placeholder)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # En una implementación real, verificaríamos la API key
        api_key = request.headers.get('X-API-Key')
        
        if not api_key and current_app.config.get('REQUIRE_API_KEY', False):
            return jsonify({
                "error": "API Key requerida"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
