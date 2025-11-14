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
    
    # Configuración básica usando variables de entorno
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecreto')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    app.config['MONGO_DB'] = os.getenv('MONGO_DB', 'sistema_alerta')
    app.config['MONGO_COLLECTION'] = 'mediciones'
    
    # Configurar CORS usando variables de entorno
    cors_origins_env = os.getenv('CORS_ORIGINS', '')
    
    # Orígenes locales para desarrollo
    local_origins = [
        'http://localhost:3000',    # React dev server
        'http://127.0.0.1:3000',
        'http://localhost:8080',    # Vue/otros
        'http://127.0.0.1:8080',
        'http://localhost:5173',    # Vite
        'http://127.0.0.1:5173',
        'http://localhost:4200',    # Angular
        'http://127.0.0.1:4200'
    ]
    
    # Función para verificar si un origen es una IP local o localhost
    def is_local_origin(origin):
        """Verifica si un origen es localhost o una IP de red local"""
        if not origin:
            return False
        origin_lower = origin.lower()
        # Verificar localhost
        if 'localhost' in origin_lower or '127.0.0.1' in origin_lower:
            return True
        # Verificar IPs de red local (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
        import re
        ip_pattern = r'http[s]?://(\d+\.\d+\.\d+\.\d+)'
        match = re.search(ip_pattern, origin_lower)
        if match:
            ip = match.group(1)
            parts = ip.split('.')
            if len(parts) == 4:
                first_octet = int(parts[0])
                second_octet = int(parts[1])
                # 10.0.0.0/8, 192.168.0.0/16, 172.16.0.0/12
                if (first_octet == 10 or 
                    (first_octet == 192 and second_octet == 168) or
                    (first_octet == 172 and 16 <= second_octet <= 31)):
                    return True
        return False
    
    if cors_origins_env:
        # En producción, usar las URLs de CORS desde variables de entorno
        # Pero siempre incluir localhost para desarrollo local
        cors_origins = [origin.strip() for origin in cors_origins_env.split(',')]
        # Agregar localhost si no está ya incluido (para desarrollo)
        for local_origin in local_origins:
            if local_origin not in cors_origins:
                cors_origins.append(local_origin)
    else:
        # En desarrollo, usar configuración local
        cors_origins = local_origins
    
    # Configurar CORS con Flask-CORS
    # Usar una función para validar orígenes dinámicamente
    def cors_origin_validator(origin, request):
        """Validador dinámico de orígenes CORS"""
        if not origin:
            return False
        # Permitir si está en la lista o si es una IP local
        return origin in cors_origins or is_local_origin(origin)
    
    CORS(app, 
         origins=cors_origin_validator,
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
        
        # Permitir el origen si está en la lista o si es una IP local
        if origin:
            if origin in cors_origins or is_local_origin(origin):
                response.headers['Access-Control-Allow-Origin'] = origin
            elif cors_origins:
                response.headers['Access-Control-Allow-Origin'] = cors_origins[0]
        elif cors_origins:
            response.headers['Access-Control-Allow-Origin'] = cors_origins[0]
        
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        return response
    
    # Log de configuración CORS
    app.logger.info(f"CORS configurado con orígenes: {cors_origins}")
    
    # Inicializar WebSocket
    from app.services.websocket_service import websocket_service
    websocket_service.init_app(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Inicializar conexión a base de datos (no bloqueante)
    try:
        init_database(app)
    except Exception as e:
        app.logger.warning(f"⚠️ No se pudo conectar a la base de datos al iniciar: {e}")
        app.logger.info("🔄 La aplicación continuará sin conexión inicial a BD")
    
    # Log de inicio de aplicación
    app.logger.info(f"Aplicación iniciada en modo: {config_name or 'development'}")
    
    return app

def init_database(app):
    """
    Inicializar y verificar conexión a MongoDB
    """
    try:
        from pymongo import MongoClient
        
        mongo_uri = app.config['MONGO_URI']
        db_name = app.config['MONGO_DB']
        
        # Crear conexión a MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Verificar conexión
        client.admin.command('ping')
        
        # Crear colecciones si no existen
        collections = ['mediciones', 'sensores', 'alertas', 'usuarios']
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                app.logger.info(f"✅ Colección '{collection_name}' creada en la base de datos")
        
        # Crear índices geoespaciales
        try:
            db['mediciones'].create_index([("location", "2dsphere")])
            db['sensores'].create_index([("location", "2dsphere")])
            app.logger.info("✅ Índices geoespaciales creados correctamente")
        except Exception as e:
            app.logger.warning(f"⚠️ No se pudieron crear índices geoespaciales: {e}")
        
        app.logger.info(f"✅ Conexión a MongoDB establecida: {db_name}")
        app.logger.info(f"✅ URI de MongoDB: {mongo_uri}")
        
        # Cerrar conexión temporal
        client.close()
        
    except Exception as e:
        app.logger.error(f"❌ Error conectando a MongoDB: {e}")
        app.logger.error(f"❌ URI de MongoDB: {mongo_uri}")
        app.logger.error(f"❌ Base de datos: {db_name}")
        raise

def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""
    from app.api.compatibility_routes import compatibility_bp
    from app.api.alerts_routes import alerts_bp
    from app.api.geospatial_routes import geospatial_bp
    from app.api.health_routes import health_bp
    
    # Registrar blueprint de compatibilidad (SIN prefijo para mantener rutas exactas)
    app.register_blueprint(compatibility_bp)
    
    # Registrar blueprint de alertas (CON prefijo /api/v1)
    app.register_blueprint(alerts_bp)
    
    # Registrar blueprint de operaciones geoespaciales (CON prefijo /api)
    app.register_blueprint(geospatial_bp)
    
    # Registrar blueprint de health checks (SIN prefijo para rutas directas)
    app.register_blueprint(health_bp)
    
    # Log de blueprints registrados
    app.logger.info("Blueprints registrados correctamente")
    app.logger.info("Blueprint de compatibilidad registrado - /api/login disponible")
    app.logger.info("Blueprint de alertas registrado - /api/v1/alertas disponible")
    app.logger.info("Blueprint geoespacial registrado - /api/alertas disponible")
    app.logger.info("Blueprint de health registrado - /api/health disponible")
