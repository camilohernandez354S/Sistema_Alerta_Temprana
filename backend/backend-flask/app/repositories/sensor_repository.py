"""
Repository pattern para acceso a datos de sensores
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from flask import current_app

from app.models.sensor_model import (
    SensorDocumentGuardado, 
    SensorDocumentObtenido, 
    SensorDocumentRangoTiempo
)

class SensorRepository:
    """Repository para operaciones CRUD de sensores"""
    
    def __init__(self, client: MongoClient, db_name: str, collection_name: str):
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
            # Índice en timestamp para consultas temporales
            self.collection.create_index("timestamp")
            # Índice en estado para estadísticas
            self.collection.create_index("estado")
            # Índice compuesto para consultas frecuentes
            self.collection.create_index([("timestamp", -1), ("estado", 1)])
            
            current_app.logger.info("Índices de MongoDB verificados/creados")
        except Exception as e:
            current_app.logger.warning(f"Error creando índices: {e}")
    
    def insert_one(self, document: SensorDocumentGuardado) -> Optional[str]:
        """
        Insertar un documento
        
        Args:
            document: Documento a insertar
            
        Returns:
            Optional[str]: ID del documento insertado
        """
        try:
            result = self.collection.insert_one(document.dict())
            current_app.logger.debug(f"Documento insertado con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            current_app.logger.error(f"Error insertando documento: {e}")
            return None
    
    def find_all(self, limit: Optional[int] = None) -> List[SensorDocumentObtenido]:
        """
        Obtener todos los documentos
        
        Args:
            limit: Límite de documentos a retornar
            
        Returns:
            List[SensorDocumentObtenido]: Lista de documentos
        """
        try:
            cursor = self.collection.find().sort("_id", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            return [SensorDocumentObtenido(**doc) for doc in cursor]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo documentos: {e}")
            return []
    
    def find_by_time_range(self, start_time: str, end_time: Optional[str] = None) -> List[SensorDocumentRangoTiempo]:
        """
        Obtener documentos en un rango de tiempo
        
        Args:
            start_time: Fecha de inicio
            end_time: Fecha de fin (opcional)
            
        Returns:
            List[SensorDocumentRangoTiempo]: Lista de documentos
        """
        try:
            query = {"timestamp": {"$gte": start_time}}
            if end_time:
                query["timestamp"]["$lte"] = end_time
            
            cursor = self.collection.find(query).sort("timestamp", 1)
            return [SensorDocumentRangoTiempo(**doc) for doc in cursor]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo documentos por rango: {e}")
            return []
    
    def find_latest(self) -> Optional[SensorDocumentObtenido]:
        """
        Obtener el último documento
        
        Returns:
            Optional[SensorDocumentObtenido]: Último documento o None
        """
        try:
            doc = self.collection.find().sort("_id", -1).limit(1).next()
            return SensorDocumentObtenido(**doc) if doc else None
        except StopIteration:
            current_app.logger.info("No se encontraron documentos")
            return None
        except Exception as e:
            current_app.logger.error(f"Error obteniendo último documento: {e}")
            return None
    
    def find_by_estado(self, estado: str) -> List[SensorDocumentObtenido]:
        """
        Obtener documentos por estado
        
        Args:
            estado: Estado a filtrar
            
        Returns:
            List[SensorDocumentObtenido]: Lista de documentos
        """
        try:
            cursor = self.collection.find({"estado": estado}).sort("timestamp", -1)
            return [SensorDocumentObtenido(**doc) for doc in cursor]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo documentos por estado: {e}")
            return []
    
    def count_by_estado(self) -> Dict[str, int]:
        """
        Contar documentos por estado
        
        Returns:
            Dict[str, int]: Conteo por estado
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$estado",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            # Inicializar contadores
            stats = {"sequia": 0, "normal": 0, "inundacion": 0}
            
            # Llenar contadores normalizando nombres
            for item in result:
                estado = item["_id"]
                estado_normalizado = estado.replace('í', 'i').replace('ó', 'o')
                if estado_normalizado in stats:
                    stats[estado_normalizado] = item["count"]
            
            return stats
        except Exception as e:
            current_app.logger.error(f"Error contando por estado: {e}")
            return {"sequia": 0, "normal": 0, "inundacion": 0}
    
    def get_statistics_for_period(self, hours: int = 24) -> Dict[str, Any]:
        """
        Obtener estadísticas para un período
        
        Args:
            hours: Número de horas hacia atrás
            
        Returns:
            Dict[str, Any]: Estadísticas del período
        """
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time_str}}},
                {"$group": {
                    "_id": None,
                    "max_nivel": {"$max": "$nivel_agua"},
                    "min_nivel": {"$min": "$nivel_agua"},
                    "avg_nivel": {"$avg": "$nivel_agua"},
                    "total_lecturas": {"$sum": 1},
                    "alertas": {
                        "$sum": {
                            "$cond": [
                                {"$or": [
                                    {"$eq": ["$estado", "sequía"]},
                                    {"$eq": ["$estado", "inundación"]}
                                ]},
                                1,
                                0
                            ]
                        }
                    }
                }}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                return {
                    "maximo": round(stats.get("max_nivel", 0), 2),
                    "minimo": round(stats.get("min_nivel", 0), 2),
                    "promedio": round(stats.get("avg_nivel", 0), 2),
                    "alertas_activas": stats.get("alertas", 0),
                    "lecturas_totales": stats.get("total_lecturas", 0)
                }
            else:
                return {
                    "maximo": 0,
                    "minimo": 0,
                    "promedio": 0,
                    "alertas_activas": 0,
                    "lecturas_totales": 0
                }
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                "maximo": 0,
                "minimo": 0,
                "promedio": 0,
                "alertas_activas": 0,
                "lecturas_totales": 0
            }
    
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
            current_app.logger.error(f"Health check fallido: {e}")
            return False

    # =============================================================================
    # NUEVOS MÉTODOS PARA DATOS ESTRUCTURADOS DEL ARDUINO
    # =============================================================================

    def guardar_lectura_arduino(self, documento: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Guardar una lectura del Arduino en la colección lecturas_sensor
        
        Args:
            documento: Documento con datos de la lectura
            
        Returns:
            Optional[Dict]: Documento guardado con _id o None si falla
        """
        try:
            # Obtener colección de lecturas Arduino
            lecturas_collection = self.db[current_app.config.get('MONGO_COLLECTION_LECTURAS', 'lecturas_sensor')]
            
            # Crear índices para la nueva colección si no existen
            self._ensure_lecturas_indexes(lecturas_collection)
            
            # Insertar documento
            result = lecturas_collection.insert_one(documento)
            
            if result.inserted_id:
                # Obtener documento insertado
                documento_guardado = lecturas_collection.find_one({"_id": result.inserted_id})
                current_app.logger.info(f"Lectura Arduino guardada con ID: {result.inserted_id}")
                return documento_guardado
            else:
                current_app.logger.error("Error insertando lectura Arduino")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error guardando lectura Arduino: {e}")
            return None

    def consultar_lecturas_arduino(self, limit: int = 100, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Consultar lecturas del Arduino con filtros opcionales
        
        Args:
            limit: Límite de resultados
            since: Timestamp de inicio en formato ISO 8601
            
        Returns:
            List[Dict]: Lista de lecturas ordenadas por timestamp desc
        """
        try:
            # Obtener colección de lecturas Arduino
            lecturas_collection = self.db[current_app.config.get('MONGO_COLLECTION_LECTURAS', 'lecturas_sensor')]
            
            # Construir filtro de consulta
            filtro = {}
            if since:
                try:
                    # Convertir timestamp ISO 8601 a datetime
                    since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
                    filtro["timestamp"] = {"$gte": since_datetime.isoformat() + 'Z'}
                except ValueError:
                    current_app.logger.warning(f"Timestamp 'since' inválido: {since}")
            
            # Consultar con ordenamiento descendente por timestamp
            cursor = lecturas_collection.find(filtro).sort("timestamp", -1).limit(limit)
            
            # Convertir a lista y limpiar ObjectId
            lecturas = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])  # Convertir ObjectId a string
                lecturas.append(doc)
            
            current_app.logger.info(f"Consultadas {len(lecturas)} lecturas Arduino")
            return lecturas
            
        except Exception as e:
            current_app.logger.error(f"Error consultando lecturas Arduino: {e}")
            return []

    def _ensure_lecturas_indexes(self, collection: Collection):
        """
        Crear índices necesarios para la colección de lecturas Arduino
        
        Args:
            collection: Colección de MongoDB
        """
        try:
            # Índice en timestamp para consultas temporales
            collection.create_index("timestamp")
            # Índice en estado para estadísticas
            collection.create_index("estado")
            # Índice en intervalo_ms para análisis de frecuencia
            collection.create_index("intervalo_ms")
            # Índice compuesto para consultas frecuentes
            collection.create_index([("timestamp", -1), ("estado", 1)])
            # Índice compuesto para análisis de tendencias
            collection.create_index([("timestamp", -1), ("intervalo_ms", 1)])
            
            current_app.logger.info("Índices de colección lecturas_sensor verificados/creados")
        except Exception as e:
            current_app.logger.warning(f"Error creando índices de lecturas: {e}")