"""
Repository para operaciones CRUD de alertas
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from flask import current_app

class AlertRepository:
    """Repository para operaciones CRUD de alertas"""
    
    def __init__(self, client: MongoClient, db_name: str, collection_name: str = "alerts"):
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
            # Índice en location para consultas por ubicación
            self.collection.create_index("location")
            # Índice en status para filtrar alertas activas
            self.collection.create_index("status")
            # Índice en alert_type para consultas por tipo
            self.collection.create_index("alert_type")
            # Índice en priority para consultas por prioridad
            self.collection.create_index("priority")
            # Índice compuesto para consultas eficientes
            self.collection.create_index([("location", 1), ("status", 1)])
            self.collection.create_index([("created_at", -1)])
            
            current_app.logger.info("Índices de alertas verificados/creados")
        except Exception as e:
            current_app.logger.warning(f"Error creando índices de alertas: {e}")
    
    def insert_one(self, alert_data: Dict[str, Any]) -> Optional[str]:
        """
        Insertar una alerta
        
        Args:
            alert_data: Datos de la alerta
            
        Returns:
            Optional[str]: ID de la alerta insertada
        """
        try:
            result = self.collection.insert_one(alert_data)
            current_app.logger.debug(f"Alerta insertada con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            current_app.logger.error(f"Error insertando alerta: {e}")
            return None
    
    def find_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Buscar alerta por ID
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Optional[Dict[str, Any]]: Alerta encontrada o None
        """
        try:
            if not ObjectId.is_valid(alert_id):
                return None
            
            alert = self.collection.find_one({"_id": ObjectId(alert_id)})
            if alert:
                alert['_id'] = str(alert['_id'])
            return alert
        except Exception as e:
            current_app.logger.error(f"Error buscando alerta por ID: {e}")
            return None
    
    def find_active(self, location: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtener alertas activas
        
        Args:
            location: Filtrar por ubicación
            limit: Límite de alertas
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas activas
        """
        try:
            filter_query = {"status": "active"}
            if location:
                filter_query["location"] = location
            
            cursor = self.collection.find(filter_query).sort("created_at", -1).limit(limit)
            
            alerts = []
            for alert in cursor:
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            return alerts
        except Exception as e:
            current_app.logger.error(f"Error obteniendo alertas activas: {e}")
            return []
    
    def find_by_location(self, location: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Buscar alertas por ubicación
        
        Args:
            location: Ubicación de las alertas
            limit: Límite de alertas
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas
        """
        try:
            cursor = self.collection.find({"location": location}).sort("created_at", -1).limit(limit)
            
            alerts = []
            for alert in cursor:
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            return alerts
        except Exception as e:
            current_app.logger.error(f"Error buscando alertas por ubicación: {e}")
            return []
    
    def find_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Buscar alertas por estado
        
        Args:
            status: Estado de las alertas
            limit: Límite de alertas
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas
        """
        try:
            cursor = self.collection.find({"status": status}).sort("created_at", -1).limit(limit)
            
            alerts = []
            for alert in cursor:
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            return alerts
        except Exception as e:
            current_app.logger.error(f"Error buscando alertas por estado: {e}")
            return []
    
    def update_one(self, alert_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Actualizar una alerta
        
        Args:
            alert_id: ID de la alerta
            update_data: Datos a actualizar
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            if not ObjectId.is_valid(alert_id):
                return False
            
            result = self.collection.update_one(
                {"_id": ObjectId(alert_id)},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                current_app.logger.debug(f"Alerta {alert_id} actualizada exitosamente")
            
            return success
        except Exception as e:
            current_app.logger.error(f"Error actualizando alerta: {e}")
            return False
    
    def find_last_alert_by_config(self, config_id: str, location: str) -> Optional[Dict[str, Any]]:
        """
        Buscar la última alerta por configuración y ubicación
        
        Args:
            config_id: ID de la configuración
            location: Ubicación
            
        Returns:
            Optional[Dict[str, Any]]: Última alerta o None
        """
        try:
            alert = self.collection.find_one(
                {"location": location},
                sort=[("created_at", -1)]
            )
            
            if alert:
                alert['_id'] = str(alert['_id'])
            return alert
        except Exception as e:
            current_app.logger.error(f"Error buscando última alerta: {e}")
            return None
    
    def get_summary(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener resumen de alertas
        
        Args:
            location: Filtrar por ubicación
            
        Returns:
            Dict[str, Any]: Resumen de alertas
        """
        try:
            match_stage = {}
            if location:
                match_stage["location"] = location
            
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": None,
                        "total_alerts": {"$sum": 1},
                        "active_alerts": {
                            "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                        },
                        "resolved_alerts": {
                            "$sum": {"$cond": [{"$eq": ["$status", "resolved"]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                summary = result[0]
                summary.pop("_id", None)
            else:
                summary = {
                    "total_alerts": 0,
                    "active_alerts": 0,
                    "resolved_alerts": 0
                }
            
            # Obtener alertas por tipo
            type_pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": "$alert_type",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            type_result = list(self.collection.aggregate(type_pipeline))
            summary["alerts_by_type"] = {item["_id"]: item["count"] for item in type_result}
            
            # Obtener alertas por prioridad
            priority_pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": "$priority",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            priority_result = list(self.collection.aggregate(priority_pipeline))
            summary["alerts_by_priority"] = {item["_id"]: item["count"] for item in priority_result}
            
            return summary
        except Exception as e:
            current_app.logger.error(f"Error obteniendo resumen de alertas: {e}")
            return {
                "total_alerts": 0,
                "active_alerts": 0,
                "resolved_alerts": 0,
                "alerts_by_type": {},
                "alerts_by_priority": {}
            }
    
    def get_location_stats(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Obtener estadísticas por ubicación
        
        Args:
            location: Ubicación
            
        Returns:
            Optional[Dict[str, Any]]: Estadísticas de la ubicación
        """
        try:
            # Contar alertas por ubicación
            alert_count = self.collection.count_documents({"location": location})
            
            # Obtener última alerta
            last_alert = self.collection.find_one(
                {"location": location},
                sort=[("created_at", -1)]
            )
            
            # Obtener nivel promedio de alertas
            pipeline = [
                {"$match": {"location": location}},
                {
                    "$group": {
                        "_id": None,
                        "avg_level": {"$avg": "$nivel_agua"},
                        "max_level": {"$max": "$nivel_agua"},
                        "min_level": {"$min": "$nivel_agua"}
                    }
                }
            ]
            
            stats_result = list(self.collection.aggregate(pipeline))
            
            stats = {
                "location": location,
                "alert_count": alert_count,
                "last_alert": last_alert["created_at"] if last_alert else None,
                "status": "normal"  # Por defecto
            }
            
            if stats_result:
                stats.update({
                    "avg_level": stats_result[0]["avg_level"],
                    "max_level": stats_result[0]["max_level"],
                    "min_level": stats_result[0]["min_level"]
                })
            
            # Determinar estado basado en alertas recientes
            recent_alerts = self.collection.count_documents({
                "location": location,
                "status": "active",
                "created_at": {
                    "$gte": (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
                }
            })
            
            if recent_alerts > 0:
                stats["status"] = "alert"
            
            return stats
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas de ubicación: {e}")
            return None
