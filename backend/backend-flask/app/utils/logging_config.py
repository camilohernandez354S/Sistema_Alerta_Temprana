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
    
    # Configurar formato estructurado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Formato JSON para logs estructurados (opcional)
    json_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", '
        '"function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}'
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

class PredictionLogger:
    """Logger contextual para predicciones con métricas específicas"""
    
    def __init__(self, logger_name: str = 'prediction_service'):
        self.logger = logging.getLogger(logger_name)
    
    def log_prediction_start(self, data_points: int, horizons: list, window_minutes: int):
        """Log inicio de predicción"""
        self.logger.info(
            f"INICIO_PREDICCION - data_points={data_points}, "
            f"horizons={horizons}, window_minutes={window_minutes}"
        )
    
    def log_data_preprocessing(self, original_count: int, cleaned_count: int, outliers_removed: int = 0):
        """
        Log detallado del preprocesamiento de datos de sensores
        
        Registra las estadísticas del proceso de limpieza y preprocesamiento de datos,
        incluyendo conteos originales, datos limpios finales y outliers removidos.
        
        Args:
            original_count (int): Número total de registros de datos originales
            cleaned_count (int): Número final de registros después del preprocesamiento
            outliers_removed (int, optional): Número de outliers detectados y removidos.
                                            Defaults to 0.
        
        Example:
            >>> logger.log_data_preprocessing(
            ...     original_count=150,
            ...     cleaned_count=142,
            ...     outliers_removed=8
            ... )
        """
        reduction_percentage = ((original_count - cleaned_count) / original_count * 100) if original_count > 0 else 0
        self.logger.info(
            f"PREPROCESAMIENTO - original={original_count}, "
            f"limpios={cleaned_count}, outliers_removidos={outliers_removed}, "
            f"reducción={reduction_percentage:.1f}%"
        )
    
    def log_signal_analysis(self, slope: float, r_squared: float, trend: str, window_points: int):
        """Log análisis de señales"""
        self.logger.info(
            f"ANALISIS_SENALES - pendiente={slope:.3f}, r_squared={r_squared:.3f}, "
            f"tendencia={trend}, puntos_ventana={window_points}"
        )
    
    def log_prediction_result(self, horizon: int, predicted_level: float, confidence: float, state: str):
        """Log resultado de predicción individual"""
        self.logger.info(
            f"PREDICCION_HORIZONTE - horizon_min={horizon}, "
            f"nivel_predicho={predicted_level:.2f}, confianza={confidence:.2f}, estado={state}"
        )
    
    def log_prediction_complete(self, total_horizons: int, avg_confidence: float, processing_time: float):
        """Log completación de predicción"""
        self.logger.info(
            f"PREDICCION_COMPLETA - total_horizons={total_horizons}, "
            f"confianza_promedio={avg_confidence:.2f}, tiempo_procesamiento={processing_time:.3f}s"
        )
    
    def log_warning_insufficient_data(self, available_points: int, required_points: int):
        """Log advertencia de datos insuficientes"""
        self.logger.warning(
            f"DATOS_INSUFICIENTES - disponibles={available_points}, requeridos={required_points}"
        )
    
    def log_error_prediction(self, error_msg: str, error_type: str = "PREDICTION_ERROR"):
        """Log error en predicción"""
        self.logger.error(f"ERROR_PREDICCION - tipo={error_type}, mensaje={error_msg}")

class APILogger:
    """Logger contextual para endpoints de API"""
    
    def __init__(self, logger_name: str = 'api'):
        self.logger = logging.getLogger(logger_name)
    
    def log_endpoint_request(self, endpoint: str, method: str, params: dict = None, user_agent: str = None):
        """Log request a endpoint"""
        params_str = f", params={params}" if params else ""
        user_agent_str = f", user_agent={user_agent}" if user_agent else ""
        self.logger.info(f"API_REQUEST - {method} {endpoint}{params_str}{user_agent_str}")
    
    def log_endpoint_response(self, endpoint: str, status_code: int, response_time: float, data_size: int = None):
        """Log response de endpoint"""
        size_str = f", data_size={data_size}" if data_size else ""
        self.logger.info(f"API_RESPONSE - {endpoint} - status={status_code}, time={response_time:.3f}s{size_str}")
    
    def log_endpoint_error(self, endpoint: str, error_msg: str, error_code: str = None):
        """Log error de endpoint"""
        code_str = f", error_code={error_code}" if error_code else ""
        self.logger.error(f"API_ERROR - {endpoint} - {error_msg}{code_str}")
