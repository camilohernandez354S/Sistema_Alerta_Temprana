"""
Configuración de logging estructurado
"""
import logging
import logging.handlers
import os
from datetime import datetime

def configure_logging(app):
    """Configurar sistema de logging para la aplicación"""
    
    # Obtener configuración
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_file = app.config.get('LOG_FILE', 'app.log')
    
    # Crear directorio de logs si no existe
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Configurar handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(logs_dir, log_file),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Configurar logger de la aplicación
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # Evitar duplicación de logs
    app.logger.propagate = False
    
    # Configurar loggers de librerías externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    
    app.logger.info("Sistema de logging configurado correctamente")

class RequestLogger:
    """Middleware para logging de requests"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar middleware con la aplicación"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Log antes de procesar la request"""
        from flask import request, g
        g.start_time = datetime.now()
        
        if request.endpoint != 'health':  # No logear health checks
            current_app.logger.info(
                f"Request: {request.method} {request.path} from {request.remote_addr}"
            )
    
    def after_request(self, response):
        """Log después de procesar la request"""
        from flask import request, g, current_app
        
        if hasattr(g, 'start_time') and request.endpoint != 'health':
            duration = (datetime.now() - g.start_time).total_seconds()
            current_app.logger.info(
                f"Response: {request.method} {request.path} - "
                f"Status: {response.status_code} - Duration: {duration:.3f}s"
            )
        
        return response
