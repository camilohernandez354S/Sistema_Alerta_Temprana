"""
Application Factory Pattern para Flask
"""
from flask import Flask, request
from flask_cors import CORS
import logging
import os

def create_app(config_name=None):
    """
    Application Factory para crear la aplicación Flask
    """
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'supersecreto'
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
    app.config['MONGO_DB'] = 'sistema_alerta'
    app.config['MONGO_COLLECTION'] = 'mediciones'
    
    # Configurar CORS de manera simple y robusta - Combinando ambas configuraciones
    cors_origins = [
        'http://localhost:3000',    # React dev server
        'http://127.0.0.1:3000',
        'http://localhost:8080',    # Vue/otros
        'http://127.0.0.1:8080',
        'http://localhost:5173',    # Vite
        'http://127.0.0.1:5173',
        'http://localhost:4200',    # Angular
        'http://127.0.0.1:4200'
    ]
    
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
        allowed_origins = [
            'http://localhost:3000', 'http://127.0.0.1:3000',
            'http://localhost:8080', 'http://127.0.0.1:8080',
            'http://localhost:5173', 'http://127.0.0.1:5173',
            'http://localhost:4200', 'http://127.0.0.1:4200'
        ]
        
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
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Log de inicio de aplicación
    app.logger.info(f"Aplicación iniciada en modo: {config_name or 'development'}")
    
    return app

def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""
    from app.api.compatibility_routes import compatibility_bp
    from app.api.alerts_routes import alerts_bp
    
    # Registrar blueprint de compatibilidad (SIN prefijo para mantener rutas exactas)
    app.register_blueprint(compatibility_bp)
    
    # Registrar blueprint de alertas (CON prefijo /api/v1)
    app.register_blueprint(alerts_bp)
    
    # Log de blueprints registrados
    app.logger.info("Blueprints registrados correctamente")
    app.logger.info("Blueprint de compatibilidad registrado - /api/login disponible")
    app.logger.info("Blueprint de alertas registrado - /api/v1/alertas disponible")
