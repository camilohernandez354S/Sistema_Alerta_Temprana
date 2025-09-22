"""
Manejadores centralizados de errores
"""
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import traceback

def register_error_handlers(app):
    """Registrar todos los manejadores de errores"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Manejo de peticiones mal formadas"""
        current_app.logger.warning(f"Bad request: {error}")
        return jsonify({
            "error": "Petición mal formada",
            "message": str(error.description) if hasattr(error, 'description') else "Datos inválidos"
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Manejo de recursos no encontrados"""
        current_app.logger.warning(f"Resource not found: {error}")
        return jsonify({
            "error": "Recurso no encontrado",
            "message": "El endpoint solicitado no existe"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Manejo de métodos no permitidos"""
        current_app.logger.warning(f"Method not allowed: {error}")
        return jsonify({
            "error": "Método no permitido",
            "message": "El método HTTP utilizado no está permitido para este endpoint"
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Manejo de errores internos del servidor"""
        current_app.logger.error(f"Internal server error: {error}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado"
        }), 500
    
    @app.errorhandler(ConnectionFailure)
    def mongo_connection_error(error):
        """Manejo de errores de conexión a MongoDB"""
        current_app.logger.error(f"MongoDB connection error: {error}")
        return jsonify({
            "error": "Error de conexión a la base de datos",
            "message": "No se pudo conectar a la base de datos. Intente nuevamente más tarde."
        }), 503
    
    @app.errorhandler(ServerSelectionTimeoutError)
    def mongo_timeout_error(error):
        """Manejo de timeout en conexión a MongoDB"""
        current_app.logger.error(f"MongoDB timeout error: {error}")
        return jsonify({
            "error": "Timeout de conexión a la base de datos",
            "message": "La conexión a la base de datos ha expirado. Intente nuevamente."
        }), 503
    
    @app.errorhandler(ValueError)
    def validation_error(error):
        """Manejo de errores de validación"""
        current_app.logger.warning(f"Validation error: {error}")
        return jsonify({
            "error": "Error de validación",
            "message": str(error)
        }), 400
    
    @app.errorhandler(Exception)
    def general_exception(error):
        """Manejo general de excepciones no capturadas"""
        current_app.logger.error(f"Unhandled exception: {error}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # En desarrollo, mostrar más detalles
        if app.config.get('DEBUG'):
            return jsonify({
                "error": "Error no manejado",
                "message": str(error),
                "type": type(error).__name__
            }), 500
        else:
            return jsonify({
                "error": "Error interno del servidor",
                "message": "Ha ocurrido un error inesperado"
            }), 500
