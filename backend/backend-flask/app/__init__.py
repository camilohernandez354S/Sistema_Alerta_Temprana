"""
Application Factory Pattern para Flask
"""
from flask import Flask, request
from flask_cors import CORS
import logging
import os
from config.config import get_config
from app.utils.error_handlers import register_error_handlers
from app.utils.logging_config import configure_logging
from app.services.websocket_service import websocket_service
from app.utils.rate_limiter import rate_limiter
from app.services.email_service import email_service

def create_app(config_name=None):
    """
    Application Factory para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Flask: Instancia de la aplicación configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Validar configuración en producción
    if config_name == 'production':
        config.validate_config()
    
    # Configurar CORS de manera simple y robusta
    cors_origins = ['http://localhost:8080', 'http://127.0.0.1:8080']
    
    # Configurar CORS con Flask-CORS
    CORS(app, 
         origins=cors_origins,
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin', 'Access-Control-Request-Method', 'Access-Control-Request-Headers'],
         expose_headers=['Content-Type', 'Authorization'],
         max_age=3600,
         automatic_options=True)
    
    # Agregar headers CORS adicionales para todas las respuestas
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        allowed_origins = ['http://localhost:8080', 'http://127.0.0.1:8080']
        
        if origin and origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = allowed_origins[0]
        
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        return response
    
    # Log de configuración CORS
    app.logger.info(f"CORS configurado con orígenes: {cors_origins}")
    
    # Configurar logging
    configure_logging(app)
    
    # Inicializar rate limiter
    try:
        rate_limiter._setup_redis()
        rate_limiter._setup_limiter()
        app.logger.info("Rate limiter inicializado")
    except Exception as e:
        app.logger.warning(f"Error inicializando rate limiter: {e}")
    
    # Inicializar WebSocket
    try:
        websocket_service.init_app(app)
        app.logger.info("WebSocket service inicializado")
    except Exception as e:
        app.logger.warning(f"Error inicializando WebSocket: {e}")
    
    # Inicializar Email Service
    try:
        email_service.init_app(app)
        app.logger.info("Email service inicializado")
    except Exception as e:
        app.logger.warning(f"Error inicializando Email service: {e}")
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Log de inicio de aplicación
    app.logger.info(f"Aplicación iniciada en modo: {config_name or 'development'}")
    
    return app

def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""
    from app.api.sensor_routes import sensor_bp
    from app.api.auth_routes import auth_bp
    from app.api.device_routes import device_bp
    from app.api.password_reset_routes import password_reset_bp
    from app.api.export_routes import export_bp
    
    # Registrar blueprint de sensor con prefijo
    app.register_blueprint(sensor_bp, url_prefix='/api')
    
    # Registrar blueprint de autenticación con prefijo
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Registrar blueprint de dispositivos con prefijo
    app.register_blueprint(device_bp, url_prefix='/api')
    
    # Registrar blueprint de recuperación de contraseñas
    app.register_blueprint(password_reset_bp, url_prefix='/api/auth')
    
    # Registrar blueprint de exportación
    app.register_blueprint(export_bp, url_prefix='/api/export')
    
    # Log de blueprints registrados
    app.logger.info("Blueprints registrados correctamente")
