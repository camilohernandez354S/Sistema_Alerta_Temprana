"""
Configuraciones para diferentes entornos
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'sensor_database')
    MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'sensor_readings')
    
    # Configuración de CORS - Incluir puertos 8080 (Vue CLI) y 5173 (Vite)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Configuración de la aplicación
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Configuración de JWT
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRATION_DAYS', '30'))
    
    # Configuración de Redis para rate limiting
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    
    # Configuración de Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME', 'Sistema de Monitoreo')
    
    # Configuración del frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8080')

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    
    # En desarrollo, asegurar que CORS incluya el puerto 8080
    def __init__(self):
        super().__init__()
        # Configurar CORS_ORIGINS como lista directa
        base_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173')
        if isinstance(base_origins, str):
            self.CORS_ORIGINS = [origin.strip() for origin in base_origins.split(',')]
        else:
            self.CORS_ORIGINS = base_origins if isinstance(base_origins, list) else ['http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:5173', 'http://127.0.0.1:5173']
        
        # Asegurar que los orígenes de desarrollo estén incluidos
        dev_origins = ['http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:5173', 'http://127.0.0.1:5173']
        for origin in dev_origins:
            if origin not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append(origin)

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    
    # En producción, validar que las variables críticas estén definidas
    @classmethod
    def validate_config(cls):
        required_vars = ['MONGO_URI', 'MONGO_DB', 'SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Variables de entorno faltantes: {', '.join(missing_vars)}")

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    MONGO_DB = os.getenv('MONGO_DB_TEST', 'sensor_database_test')
    LOG_LEVEL = 'DEBUG'

# Diccionario de configuraciones disponibles
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Obtener configuración por nombre"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)
