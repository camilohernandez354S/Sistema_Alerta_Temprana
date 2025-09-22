"""
Repository pattern para acceso a datos de dispositivos Arduino
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from flask import current_app

from app.models.device import (
    DeviceDocument, 
    DeviceDocumentGuardado, 
    DeviceCreate, 
    DeviceUpdate,
    DeviceStatus
)


class DeviceRepository:
    """Repository para operaciones CRUD de dispositivos Arduino"""
    
    def __init__(self, client: MongoClient, db_name: str, collection_name: str = 'devices'):
        """
        Inicializar repository
        
        Args:
            client: Cliente de MongoDB
            db_name: Nombre de la base de datos
            collection_name: Nombre de la colección
        """
        self.client = client
        self.db = client[db_name]
        self.collection: Collection = self.db[collection_name]
        
        # Crear índices si no existen
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crear índices necesarios"""
        try:
            # Índice único en puerto
            self.collection.create_index("port", unique=True)
            # Índice único en nombre
            self.collection.create_index("name", unique=True)
            # Índice en status para consultas rápidas
            self.collection.create_index("status")
            # Índice en last_seen para consultas temporales
            self.collection.create_index("last_seen")
            
            current_app.logger.info("Índices de dispositivos MongoDB verificados/creados")
        except Exception as e:
            current_app.logger.warning(f"Error creando índices de dispositivos: {e}")
    
    def insert_one(self, document: DeviceDocumentGuardado) -> Optional[str]:
        """
        Insertar un dispositivo
        
        Args:
            document: Dispositivo a insertar
            
        Returns:
            Optional[str]: ID del dispositivo insertado
        """
        try:
            result = self.collection.insert_one(document.dict())
            current_app.logger.debug(f"Dispositivo insertado con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            current_app.logger.error(f"Error insertando dispositivo: {e}")
            return None
    
    def find_all(self, limit: Optional[int] = None) -> List[DeviceDocument]:
        """
        Obtener todos los dispositivos
        
        Args:
            limit: Límite de dispositivos a retornar
            
        Returns:
            List[DeviceDocument]: Lista de dispositivos
        """
        try:
            cursor = self.collection.find().sort("created_at", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            return [DeviceDocument(**doc) for doc in cursor]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo dispositivos: {e}")
            return []
    
    def find_by_id(self, device_id: str) -> Optional[DeviceDocument]:
        """
        Obtener dispositivo por ID
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            Optional[DeviceDocument]: Dispositivo encontrado o None
        """
        try:
            if not ObjectId.is_valid(device_id):
                return None
                
            doc = self.collection.find_one({"_id": ObjectId(device_id)})
            return DeviceDocument(**doc) if doc else None
        except Exception as e:
            current_app.logger.error(f"Error obteniendo dispositivo por ID: {e}")
            return None
    
    def find_by_port(self, port: str) -> Optional[DeviceDocument]:
        """
        Obtener dispositivo por puerto
        
        Args:
            port: Puerto del dispositivo
            
        Returns:
            Optional[DeviceDocument]: Dispositivo encontrado o None
        """
        try:
            doc = self.collection.find_one({"port": port})
            return DeviceDocument(**doc) if doc else None
        except Exception as e:
            current_app.logger.error(f"Error obteniendo dispositivo por puerto: {e}")
            return None
    
    def find_by_status(self, status: DeviceStatus) -> List[DeviceDocument]:
        """
        Obtener dispositivos por estado
        
        Args:
            status: Estado a filtrar
            
        Returns:
            List[DeviceDocument]: Lista de dispositivos
        """
        try:
            cursor = self.collection.find({"status": status.value}).sort("last_seen", -1)
            return [DeviceDocument(**doc) for doc in cursor]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo dispositivos por estado: {e}")
            return []
    
    def update_by_id(self, device_id: str, update_data: DeviceUpdate) -> Optional[DeviceDocument]:
        """
        Actualizar dispositivo por ID
        
        Args:
            device_id: ID del dispositivo
            update_data: Datos a actualizar
            
        Returns:
            Optional[DeviceDocument]: Dispositivo actualizado o None
        """
        try:
            if not ObjectId.is_valid(device_id):
                return None
            
            # Preparar datos de actualización
            update_dict = {}
            if update_data.name is not None:
                update_dict['name'] = update_data.name
            if update_data.config is not None:
                update_dict['config'] = update_data.config
            
            if not update_dict:
                return self.find_by_id(device_id)
            
            update_dict['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.collection.update_one(
                {"_id": ObjectId(device_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return self.find_by_id(device_id)
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error actualizando dispositivo: {e}")
            return None
    
    def update_status(self, device_id: str, status: DeviceStatus, last_seen: Optional[str] = None) -> bool:
        """
        Actualizar estado de un dispositivo
        
        Args:
            device_id: ID del dispositivo
            status: Nuevo estado
            last_seen: Última vez visto (opcional)
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            if not ObjectId.is_valid(device_id):
                return False
            
            update_data = {
                'status': status.value,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if last_seen:
                update_data['last_seen'] = last_seen
            else:
                update_data['last_seen'] = datetime.utcnow().isoformat()
            
            result = self.collection.update_one(
                {"_id": ObjectId(device_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Error actualizando estado del dispositivo: {e}")
            return False
    
    def update_status_by_port(self, port: str, status: DeviceStatus, last_seen: Optional[str] = None) -> bool:
        """
        Actualizar estado de un dispositivo por puerto
        
        Args:
            port: Puerto del dispositivo
            status: Nuevo estado
            last_seen: Última vez visto (opcional)
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            update_data = {
                'status': status.value,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if last_seen:
                update_data['last_seen'] = last_seen
            else:
                update_data['last_seen'] = datetime.utcnow().isoformat()
            
            result = self.collection.update_one(
                {"port": port},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Error actualizando estado del dispositivo por puerto: {e}")
            return False
    
    def create_device(self, device_data: DeviceCreate) -> Optional[DeviceDocument]:
        """
        Crear un nuevo dispositivo
        
        Args:
            device_data: Datos del dispositivo a crear
            
        Returns:
            Optional[DeviceDocument]: Dispositivo creado o None
        """
        try:
            # Verificar que no exista un dispositivo con el mismo puerto
            existing = self.find_by_port(device_data.port)
            if existing:
                current_app.logger.warning(f"Ya existe un dispositivo en el puerto {device_data.port}")
                return None
            
            # Crear documento para guardar
            now = datetime.utcnow().isoformat()
            device_doc = DeviceDocumentGuardado(
                name=device_data.name,
                port=device_data.port,
                status=DeviceStatus.INACTIVE,
                config=device_data.config,
                created_at=now,
                updated_at=now
            )
            
            device_id = self.insert_one(device_doc)
            if device_id:
                return self.find_by_id(device_id)
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creando dispositivo: {e}")
            return None
    
    def get_devices_status(self) -> List[Dict[str, Any]]:
        """
        Obtener estado de todos los dispositivos para la API
        
        Returns:
            List[Dict[str, Any]]: Lista de dispositivos con su estado
        """
        try:
            devices = self.find_all()
            return [device.dict() for device in devices]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estado de dispositivos: {e}")
            return []
    
    def get_active_devices_count(self) -> int:
        """
        Contar dispositivos activos
        
        Returns:
            int: Número de dispositivos activos
        """
        try:
            return self.collection.count_documents({"status": DeviceStatus.ACTIVE.value})
        except Exception as e:
            current_app.logger.error(f"Error contando dispositivos activos: {e}")
            return 0
    
    def get_inactive_devices_count(self) -> int:
        """
        Contar dispositivos inactivos
        
        Returns:
            int: Número de dispositivos inactivos
        """
        try:
            return self.collection.count_documents({"status": DeviceStatus.INACTIVE.value})
        except Exception as e:
            current_app.logger.error(f"Error contando dispositivos inactivos: {e}")
            return 0
    
    def health_check(self) -> bool:
        """
        Verificar estado de la conexión
        
        Returns:
            bool: True si la conexión está activa
        """
        try:
            self.client.server_info()
            return True
        except Exception as e:
            current_app.logger.error(f"Health check de dispositivos fallido: {e}")
            return False
