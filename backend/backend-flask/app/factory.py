"""
Factory para crear instancias de servicios y repositorios
"""
from pymongo import MongoClient
from flask import current_app

from app.repositories.sensor_repository import SensorRepository
from app.services.sensor_service import SensorService
from app.controllers.sensor_controller import SensorController
from app.utils.rate_limiter import rate_limiter
from app.services.websocket_service import websocket_service
from app.services.email_service import email_service

class ServiceFactory:
    """Factory para crear e inyectar dependencias"""
    
    def __init__(self):
        """Inicializar factory"""
        self._mongo_client = None
        self._sensor_repository = None
        self._sensor_service = None
        self._sensor_controller = None
        self._rate_limiter = None
        self._websocket_service = None
        self._email_service = None
    
    @property
    def mongo_client(self) -> MongoClient:
        """Obtener cliente de MongoDB (singleton)"""
        if self._mongo_client is None:
            mongo_uri = current_app.config['MONGO_URI']
            self._mongo_client = MongoClient(mongo_uri)
            
            # Verificar conexión
            try:
                self._mongo_client.server_info()
                current_app.logger.info("✅ Conexión a MongoDB establecida")
            except Exception as e:
                current_app.logger.error(f"❌ Error conectando a MongoDB: {e}")
                raise
                
        return self._mongo_client
    
    @property
    def sensor_repository(self) -> SensorRepository:
        """Obtener repository de sensores (singleton)"""
        if self._sensor_repository is None:
            self._sensor_repository = SensorRepository(
                client=self.mongo_client,
                db_name=current_app.config['MONGO_DB'],
                collection_name=current_app.config['MONGO_COLLECTION']
            )
        return self._sensor_repository
    
    @property
    def sensor_service(self) -> SensorService:
        """Obtener servicio de sensores (singleton)"""
        if self._sensor_service is None:
            self._sensor_service = SensorService(
                repository=self.sensor_repository
            )
        return self._sensor_service
    
    @property
    def sensor_controller(self) -> SensorController:
        """Obtener controlador de sensores (singleton)"""
        if self._sensor_controller is None:
            self._sensor_controller = SensorController(
                sensor_service=self.sensor_service
            )
        return self._sensor_controller
    
    @property
    def rate_limiter(self):
        """Obtener rate limiter (singleton)"""
        if self._rate_limiter is None:
            self._rate_limiter = rate_limiter
        return self._rate_limiter
    
    @property
    def websocket_service(self):
        """Obtener servicio WebSocket (singleton)"""
        if self._websocket_service is None:
            self._websocket_service = websocket_service
        return self._websocket_service
    
    @property
    def email_service(self):
        """Obtener servicio de email (singleton)"""
        if self._email_service is None:
            self._email_service = email_service
        return self._email_service
    
    def cleanup(self):
        """Limpiar recursos"""
        if self._mongo_client:
            self._mongo_client.close()
            current_app.logger.info("Conexión a MongoDB cerrada")

# Instancia global del factory
service_factory = ServiceFactory()
