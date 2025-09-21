"""
Middleware para rate limiting usando Redis
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import current_app
import redis
import logging
from typing import Optional

class RateLimiter:
    """Clase para manejo de rate limiting"""
    
    def __init__(self):
        """Inicializar rate limiter"""
        self.limiter: Optional[Limiter] = None
        self.redis_client: Optional[redis.Redis] = None
        self._logger = logging.getLogger(__name__)
        self._logger.info("RateLimiter inicializado")
    
    def _log(self, level: str, message: str):
        """
        Método helper para logging que funciona con o sin contexto de Flask
        
        Args:
            level: Nivel de log (info, warning, error, debug)
            message: Mensaje a loggear
        """
        try:
            # Intentar usar el logger de Flask si está disponible
            flask_logger = current_app.logger
            getattr(flask_logger, level)(message)
        except RuntimeError:
            # Si no hay contexto de Flask, usar el logger estándar
            getattr(self._logger, level)(message)
    
    def init_app(self, app):
        """Inicializar rate limiter con la aplicación Flask"""
        self._setup_redis(app)
        self._setup_limiter(app)
    
    def _setup_redis(self, app=None):
        """Configurar conexión a Redis"""
        try:
            # Usar la app proporcionada o current_app
            config_app = app or current_app
            
            if config_app.config.get('RATE_LIMIT_ENABLED', True):
                redis_url = config_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                
                # Probar conexión
                self.redis_client.ping()
                self._log("info", "✅ Conexión a Redis establecida para rate limiting")
            else:
                self._log("info", "Rate limiting deshabilitado")
                
        except Exception as e:
            self._log("warning", f"❌ No se pudo conectar a Redis: {e}")
            self.redis_client = None
    
    def _setup_limiter(self, app=None):
        """Configurar Flask-Limiter"""
        try:
            # Usar la app proporcionada o current_app
            config_app = app or current_app
            
            if self.redis_client and config_app.config.get('RATE_LIMIT_ENABLED', True):
                self.limiter = Limiter(
                    app=config_app,
                    key_func=get_remote_address,
                    storage_uri=config_app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
                    default_limits=["1000 per hour"]  # Límite global por defecto
                )
                self._log("info", "✅ Rate limiter configurado con Redis")
            else:
                # Rate limiter en memoria si Redis no está disponible
                self.limiter = Limiter(
                    app=config_app,
                    key_func=get_remote_address,
                    default_limits=["500 per hour"]  # Límite más bajo sin Redis
                )
                self._log("info", "✅ Rate limiter configurado en memoria")
                
        except Exception as e:
            self._log("error", f"❌ Error configurando rate limiter: {e}")
            self.limiter = None
    
    def is_rate_limited(self, endpoint: str, limit: str) -> bool:
        """
        Verificar si un endpoint está siendo limitado
        
        Args:
            endpoint: Nombre del endpoint
            limit: Límite a verificar (ej: "10 per minute")
            
        Returns:
            bool: True si está siendo limitado
        """
        if not self.limiter:
            return False
        
        try:
            # Verificar límite para el endpoint específico
            return self.limiter.is_rate_limited(endpoint, limit)
        except Exception as e:
            self._log("error", f"Error verificando rate limit: {e}")
            return False
    
    def get_rate_limit_info(self, endpoint: str) -> dict:
        """
        Obtener información de rate limit para un endpoint
        
        Args:
            endpoint: Nombre del endpoint
            
        Returns:
            dict: Información del rate limit
        """
        if not self.limiter:
            return {"enabled": False}
        
        try:
            # Obtener información del límite actual
            limits = self.limiter.get_limits(endpoint)
            return {
                "enabled": True,
                "limits": limits,
                "endpoint": endpoint
            }
        except Exception as e:
            self._log("error", f"Error obteniendo info de rate limit: {e}")
            return {"enabled": False, "error": str(e)}

# Instancia global del rate limiter
rate_limiter = RateLimiter()

# Decoradores de rate limiting para endpoints específicos
def auth_rate_limit():
    """Rate limit para endpoints de autenticación"""
    if rate_limiter.limiter:
        return rate_limiter.limiter.limit("5 per minute")
    return lambda f: f

def api_rate_limit():
    """Rate limit para endpoints de API generales"""
    if rate_limiter.limiter:
        return rate_limiter.limiter.limit("100 per hour")
    return lambda f: f

def strict_rate_limit():
    """Rate limit estricto para operaciones sensibles"""
    if rate_limiter.limiter:
        return rate_limiter.limiter.limit("10 per hour")
    return lambda f: f

def sensor_rate_limit():
    """Rate limit para endpoints de sensores"""
    if rate_limiter.limiter:
        return rate_limiter.limiter.limit("1000 per hour")
    return lambda f: f
