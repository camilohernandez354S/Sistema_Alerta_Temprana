"""
Repository para operaciones CRUD de usuarios
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from flask import current_app

class UserRepository:
    """Repository para operaciones CRUD de usuarios"""
    
    def __init__(self, client: MongoClient, db_name: str, collection_name: str = "users"):
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
            # Índice único en username
            self.collection.create_index("username", unique=True)
            # Índice único en email
            self.collection.create_index("email", unique=True)
            # Índice en role para consultas de permisos
            self.collection.create_index("role")
            # Índice en status para filtrar usuarios activos
            self.collection.create_index("status")
            # Índice en location para consultas por ubicación
            self.collection.create_index("location")
            
            current_app.logger.info("Índices de usuarios verificados/creados")
        except Exception as e:
            current_app.logger.warning(f"Error creando índices de usuarios: {e}")
    
    def insert_one(self, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Insertar un usuario
        
        Args:
            user_data: Datos del usuario
            
        Returns:
            Optional[str]: ID del usuario insertado
        """
        try:
            result = self.collection.insert_one(user_data)
            current_app.logger.debug(f"Usuario insertado con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            current_app.logger.error(f"Error insertando usuario: {e}")
            return None
    
    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Buscar usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Usuario encontrado o None
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            current_app.logger.error(f"Error buscando usuario por ID: {e}")
            return None
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Buscar usuario por username
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Optional[Dict[str, Any]]: Usuario encontrado o None
        """
        try:
            user = self.collection.find_one({"username": username.lower()})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            current_app.logger.error(f"Error buscando usuario por username: {e}")
            return None
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Buscar usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Usuario encontrado o None
        """
        try:
            user = self.collection.find_one({"email": email.lower()})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            current_app.logger.error(f"Error buscando usuario por email: {e}")
            return None
    
    def find_all(self, limit: Optional[int] = None, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Obtener todos los usuarios
        
        Args:
            limit: Límite de usuarios a retornar
            skip: Número de usuarios a saltar
            
        Returns:
            List[Dict[str, Any]]: Lista de usuarios
        """
        try:
            cursor = self.collection.find().skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            users = []
            for user in cursor:
                user['_id'] = str(user['_id'])
                users.append(user)
            
            return users
        except Exception as e:
            current_app.logger.error(f"Error obteniendo usuarios: {e}")
            return []
    
    def find_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Buscar usuarios por rol
        
        Args:
            role: Rol de usuario
            
        Returns:
            List[Dict[str, Any]]: Lista de usuarios
        """
        try:
            cursor = self.collection.find({"role": role})
            users = []
            for user in cursor:
                user['_id'] = str(user['_id'])
                users.append(user)
            
            return users
        except Exception as e:
            current_app.logger.error(f"Error buscando usuarios por rol: {e}")
            return []
    
    def find_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Buscar usuarios por ubicación
        
        Args:
            location: Ubicación de los usuarios
            
        Returns:
            List[Dict[str, Any]]: Lista de usuarios
        """
        try:
            cursor = self.collection.find({"location": location})
            users = []
            for user in cursor:
                user['_id'] = str(user['_id'])
                users.append(user)
            
            return users
        except Exception as e:
            current_app.logger.error(f"Error buscando usuarios por ubicación: {e}")
            return []
    
    def find_active_users(self) -> List[Dict[str, Any]]:
        """
        Obtener usuarios activos
        
        Returns:
            List[Dict[str, Any]]: Lista de usuarios activos
        """
        try:
            cursor = self.collection.find({"status": "active"})
            users = []
            for user in cursor:
                user['_id'] = str(user['_id'])
                users.append(user)
            
            return users
        except Exception as e:
            current_app.logger.error(f"Error obteniendo usuarios activos: {e}")
            return []
    
    def update_one(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Actualizar un usuario
        
        Args:
            user_id: ID del usuario
            update_data: Datos a actualizar
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                current_app.logger.debug(f"Usuario {user_id} actualizado exitosamente")
            
            return success
        except Exception as e:
            current_app.logger.error(f"Error actualizando usuario: {e}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """
        Actualizar último login de usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            update_data = {
                "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            current_app.logger.error(f"Error actualizando último login: {e}")
            return False
    
    def delete_one(self, user_id: str) -> bool:
        """
        Eliminar un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            
            success = result.deleted_count > 0
            if success:
                current_app.logger.debug(f"Usuario {user_id} eliminado exitosamente")
            
            return success
        except Exception as e:
            current_app.logger.error(f"Error eliminando usuario: {e}")
            return False
    
    def count_users(self, filter_data: Optional[Dict[str, Any]] = None) -> int:
        """
        Contar usuarios
        
        Args:
            filter_data: Filtros opcionales
            
        Returns:
            int: Número de usuarios
        """
        try:
            if filter_data:
                count = self.collection.count_documents(filter_data)
            else:
                count = self.collection.count_documents({})
            
            return count
        except Exception as e:
            current_app.logger.error(f"Error contando usuarios: {e}")
            return 0
    
    def get_users_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de usuarios
        
        Returns:
            Dict[str, Any]: Resumen de usuarios
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$role",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            summary = {
                "total": self.count_users(),
                "active": self.count_users({"status": "active"}),
                "inactive": self.count_users({"status": "inactive"}),
                "suspended": self.count_users({"status": "suspended"}),
                "by_role": {}
            }
            
            for item in result:
                summary["by_role"][item["_id"]] = item["count"]
            
            return summary
        except Exception as e:
            current_app.logger.error(f"Error obteniendo resumen de usuarios: {e}")
            return {
                "total": 0,
                "active": 0,
                "inactive": 0,
                "suspended": 0,
                "by_role": {}
            }
    
    def store_refresh_token(self, user_id: str, hashed_token: str, expires_at: datetime) -> bool:
        """
        Almacenar refresh token hasheado para un usuario
        
        Args:
            user_id: ID del usuario
            hashed_token: Token hasheado
            expires_at: Fecha de expiración
            
        Returns:
            bool: True si se almacenó correctamente
        """
        try:
            from app.models.user_model import UserResponse
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "refresh_token": hashed_token,
                        "refresh_token_expires_at": expires_at,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                current_app.logger.info(f"Refresh token almacenado para usuario: {user_id}")
            else:
                current_app.logger.warning(f"No se pudo almacenar refresh token para usuario: {user_id}")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error almacenando refresh token: {e}")
            return False
    
    def validate_refresh_token(self, hashed_token: str):
        """
        Validar refresh token y obtener usuario
        
        Args:
            hashed_token: Token hasheado
            
        Returns:
            Optional[UserResponse]: Usuario si el token es válido
        """
        try:
            from app.models.user_model import UserResponse
            
            # Buscar usuario con el refresh token
            user_data = self.collection.find_one({
                "refresh_token": hashed_token,
                "refresh_token_expires_at": {"$gt": datetime.utcnow()},
                "status": "active"
            })
            
            if user_data:
                # Convertir a UserResponse
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                del user_data['password_hash']  # No incluir hash de contraseña
                del user_data['refresh_token']  # No incluir refresh token
                del user_data['refresh_token_expires_at']
                
                current_app.logger.info(f"Refresh token válido para usuario: {user_data.get('username')}")
                return UserResponse(**user_data)
            else:
                current_app.logger.warning("Refresh token inválido o expirado")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error validando refresh token: {e}")
            return None
    
    def revoke_refresh_token(self, hashed_token: str) -> bool:
        """
        Revocar refresh token
        
        Args:
            hashed_token: Token hasheado a revocar
            
        Returns:
            bool: True si se revocó correctamente
        """
        try:
            result = self.collection.update_one(
                {"refresh_token": hashed_token},
                {
                    "$unset": {
                        "refresh_token": "",
                        "refresh_token_expires_at": ""
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                current_app.logger.info("Refresh token revocado exitosamente")
            else:
                current_app.logger.warning("No se encontró refresh token para revocar")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error revocando refresh token: {e}")
            return False