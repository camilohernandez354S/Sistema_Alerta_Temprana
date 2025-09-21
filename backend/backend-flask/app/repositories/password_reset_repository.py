"""
Repository para operaciones CRUD de tokens de reset de contraseña
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from flask import current_app

from app.models.password_reset_model import (
    PasswordResetCreate, PasswordResetResponse, PasswordResetStats,
    PasswordResetStatus
)

class PasswordResetRepository:
    """Repository para operaciones CRUD de tokens de reset"""
    
    def __init__(self, client: MongoClient, db_name: str, collection_name: str = "password_resets"):
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
            # Índice único en token
            self.collection.create_index("token", unique=True)
            # Índice en user_id para consultas por usuario
            self.collection.create_index("user_id")
            # Índice en email para consultas por email
            self.collection.create_index("email")
            # Índice en expires_at para limpieza automática
            self.collection.create_index("expires_at")
            # Índice compuesto para consultas eficientes
            self.collection.create_index([("user_id", 1), ("status", 1)])
            
            current_app.logger.info("Índices de password reset verificados/creados")
        except Exception as e:
            current_app.logger.warning(f"Error creando índices de password reset: {e}")
    
    def create_reset_token(self, reset_data: PasswordResetCreate, token: str, expires_in_hours: int = 1) -> Optional[str]:
        """
        Crear token de reset de contraseña
        
        Args:
            reset_data: Datos del reset
            token: Token generado
            expires_in_hours: Horas hasta expiración
            
        Returns:
            Optional[str]: ID del token creado o None
        """
        try:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            
            reset_doc = {
                "user_id": reset_data.user_id,
                "email": reset_data.email.lower(),
                "token": token,
                "status": PasswordResetStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "used_at": None
            }
            
            result = self.collection.insert_one(reset_doc)
            
            if result.inserted_id:
                current_app.logger.info(f"Token de reset creado para usuario: {reset_data.email}")
                return str(result.inserted_id)
            else:
                current_app.logger.error("Error creando token de reset")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error creando token de reset: {e}")
            return None
    
    def find_by_token(self, token: str) -> Optional[PasswordResetResponse]:
        """
        Buscar token de reset por token
        
        Args:
            token: Token a buscar
            
        Returns:
            Optional[PasswordResetResponse]: Token encontrado o None
        """
        try:
            reset_doc = self.collection.find_one({"token": token})
            
            if reset_doc:
                reset_doc['id'] = str(reset_doc['_id'])
                del reset_doc['_id']
                return PasswordResetResponse(**reset_doc)
            else:
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error buscando token de reset: {e}")
            return None
    
    def find_by_user_id(self, user_id: str, status: Optional[PasswordResetStatus] = None) -> List[PasswordResetResponse]:
        """
        Buscar tokens de reset por usuario
        
        Args:
            user_id: ID del usuario
            status: Estado del token (opcional)
            
        Returns:
            List[PasswordResetResponse]: Lista de tokens
        """
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status.value
            
            reset_docs = list(self.collection.find(query).sort("created_at", -1))
            
            results = []
            for doc in reset_docs:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                results.append(PasswordResetResponse(**doc))
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"Error buscando tokens por usuario: {e}")
            return []
    
    def find_by_email(self, email: str, status: Optional[PasswordResetStatus] = None) -> List[PasswordResetResponse]:
        """
        Buscar tokens de reset por email
        
        Args:
            email: Email del usuario
            status: Estado del token (opcional)
            
        Returns:
            List[PasswordResetResponse]: Lista de tokens
        """
        try:
            query = {"email": email.lower()}
            if status:
                query["status"] = status.value
            
            reset_docs = list(self.collection.find(query).sort("created_at", -1))
            
            results = []
            for doc in reset_docs:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                results.append(PasswordResetResponse(**doc))
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"Error buscando tokens por email: {e}")
            return []
    
    def mark_as_used(self, token: str) -> bool:
        """
        Marcar token como usado
        
        Args:
            token: Token a marcar
            
        Returns:
            bool: True si se marcó correctamente
        """
        try:
            result = self.collection.update_one(
                {"token": token},
                {
                    "$set": {
                        "status": PasswordResetStatus.USED.value,
                        "used_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                current_app.logger.info(f"Token de reset marcado como usado: {token}")
            else:
                current_app.logger.warning(f"No se encontró token para marcar como usado: {token}")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error marcando token como usado: {e}")
            return False
    
    def mark_as_expired(self, token: str) -> bool:
        """
        Marcar token como expirado
        
        Args:
            token: Token a marcar
            
        Returns:
            bool: True si se marcó correctamente
        """
        try:
            result = self.collection.update_one(
                {"token": token},
                {
                    "$set": {
                        "status": PasswordResetStatus.EXPIRED.value
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                current_app.logger.info(f"Token de reset marcado como expirado: {token}")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error marcando token como expirado: {e}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Limpiar tokens expirados
        
        Returns:
            int: Número de tokens eliminados
        """
        try:
            result = self.collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()},
                "status": {"$ne": PasswordResetStatus.USED.value}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                current_app.logger.info(f"Limpiados {deleted_count} tokens expirados")
            
            return deleted_count
            
        except Exception as e:
            current_app.logger.error(f"Error limpiando tokens expirados: {e}")
            return 0
    
    def invalidate_user_tokens(self, user_id: str) -> int:
        """
        Invalidar todos los tokens pendientes de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            int: Número de tokens invalidados
        """
        try:
            result = self.collection.update_many(
                {
                    "user_id": user_id,
                    "status": PasswordResetStatus.PENDING.value
                },
                {
                    "$set": {
                        "status": PasswordResetStatus.EXPIRED.value
                    }
                }
            )
            
            modified_count = result.modified_count
            if modified_count > 0:
                current_app.logger.info(f"Invalidados {modified_count} tokens para usuario: {user_id}")
            
            return modified_count
            
        except Exception as e:
            current_app.logger.error(f"Error invalidando tokens de usuario: {e}")
            return 0
    
    def get_reset_stats(self) -> PasswordResetStats:
        """
        Obtener estadísticas de reset de contraseñas
        
        Returns:
            PasswordResetStats: Estadísticas
        """
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Total de solicitudes
            total = self.collection.count_documents({})
            
            # Solicitudes pendientes
            pending = self.collection.count_documents({"status": PasswordResetStatus.PENDING.value})
            
            # Solicitudes usadas
            used = self.collection.count_documents({"status": PasswordResetStatus.USED.value})
            
            # Solicitudes expiradas
            expired = self.collection.count_documents({"status": PasswordResetStatus.EXPIRED.value})
            
            # Solicitudes de hoy
            today_requests = self.collection.count_documents({
                "created_at": {"$gte": today_start}
            })
            
            return PasswordResetStats(
                total_requests=total,
                pending_requests=pending,
                used_requests=used,
                expired_requests=expired,
                today_requests=today_requests
            )
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas de reset: {e}")
            return PasswordResetStats(
                total_requests=0,
                pending_requests=0,
                used_requests=0,
                expired_requests=0,
                today_requests=0
            )
    
    def is_rate_limited(self, email: str, max_requests_per_hour: int = 3) -> bool:
        """
        Verificar si un email está siendo rate limited
        
        Args:
            email: Email a verificar
            max_requests_per_hour: Máximo de solicitudes por hora
            
        Returns:
            bool: True si está siendo limitado
        """
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            recent_requests = self.collection.count_documents({
                "email": email.lower(),
                "created_at": {"$gte": one_hour_ago}
            })
            
            is_limited = recent_requests >= max_requests_per_hour
            
            if is_limited:
                current_app.logger.warning(f"Rate limit alcanzado para email: {email}")
            
            return is_limited
            
        except Exception as e:
            current_app.logger.error(f"Error verificando rate limit: {e}")
            return True  # En caso de error, aplicar rate limit por seguridad
