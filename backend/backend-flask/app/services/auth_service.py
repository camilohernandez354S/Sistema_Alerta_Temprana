"""
Servicio de autenticación y autorización
"""
import jwt
import bcrypt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from flask import current_app
from http import HTTPStatus

from app.models.user_model import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    TokenResponse, PasswordChange, UserRole, RefreshTokenResponse
)
from app.repositories.user_repository import UserRepository

class AuthService:
    """Servicio para autenticación y autorización"""
    
    def __init__(self, user_repository: UserRepository):
        """
        Inicializar servicio
        
        Args:
            user_repository: Repository para usuarios
        """
        self.user_repository = user_repository
        current_app.logger.info("AuthService inicializado")
    
    def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """
        Crear nuevo usuario
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            Optional[UserResponse]: Usuario creado o None
        """
        try:
            # Verificar si el usuario ya existe
            existing_user = self.user_repository.find_by_username(user_data.username)
            if existing_user:
                current_app.logger.warning(f"Usuario {user_data.username} ya existe")
                return None
            
            existing_email = self.user_repository.find_by_email(user_data.email)
            if existing_email:
                current_app.logger.warning(f"Email {user_data.email} ya existe")
                return None
            
            # Hashear contraseña
            hashed_password = self._hash_password(user_data.password)
            
            # Crear usuario
            user_dict = user_data.dict()
            user_dict['password'] = hashed_password
            user_dict['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_dict['updated_at'] = user_dict['created_at']
            
            user_id = self.user_repository.insert_one(user_dict)
            if not user_id:
                raise Exception("Error creando usuario")
            
            # Obtener usuario creado
            user = self.user_repository.find_by_id(user_id)
            if user:
                current_app.logger.info(f"Usuario {user_data.username} creado exitosamente")
                return UserResponse(**user)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creando usuario: {e}")
            return None
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[TokenResponse]:
        """
        Autenticar usuario y generar token
        
        Args:
            login_data: Datos de login
            
        Returns:
            Optional[TokenResponse]: Token de acceso o None
        """
        try:
            # Buscar usuario por username o email
            user = self.user_repository.find_by_username(login_data.username)
            if not user:
                user = self.user_repository.find_by_email(login_data.username)
            
            if not user:
                current_app.logger.warning(f"Usuario {login_data.username} no encontrado")
                return None
            
            # Verificar contraseña
            if not self._verify_password(login_data.password, user['password']):
                current_app.logger.warning(f"Contraseña incorrecta para {login_data.username}")
                return None
            
            # Verificar estado del usuario
            if user['status'] != 'active':
                current_app.logger.warning(f"Usuario {login_data.username} no está activo")
                return None
            
            # Actualizar último login
            self.user_repository.update_last_login(user['_id'])
            
            # Generar token
            token = self._generate_token(user)
            
            # Crear respuesta
            user_response = UserResponse(**user)
            token_response = TokenResponse(
                access_token=token,
                expires_in=current_app.config.get('JWT_EXPIRATION_HOURS', 24) * 3600,
                user=user_response
            )
            
            current_app.logger.info(f"Usuario {login_data.username} autenticado exitosamente")
            return token_response
            
        except Exception as e:
            current_app.logger.error(f"Error autenticando usuario: {e}")
            return None
    
    def get_current_user(self, token: str) -> Optional[UserResponse]:
        """
        Obtener usuario actual desde token
        
        Args:
            token: Token JWT
            
        Returns:
            Optional[UserResponse]: Usuario actual o None
        """
        try:
            payload = self._decode_token(token)
            if not payload:
                return None
            
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return None
            
            return UserResponse(**user)
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo usuario actual: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: UserUpdate, current_user: UserResponse) -> Optional[UserResponse]:
        """
        Actualizar usuario
        
        Args:
            user_id: ID del usuario a actualizar
            user_data: Datos a actualizar
            current_user: Usuario actual (para verificar permisos)
            
        Returns:
            Optional[UserResponse]: Usuario actualizado o None
        """
        try:
            # Verificar permisos
            if current_user.role != UserRole.ADMIN and current_user.id != user_id:
                current_app.logger.warning(f"Usuario {current_user.username} no tiene permisos para actualizar {user_id}")
                return None
            
            # Preparar datos de actualización
            update_data = user_data.dict(exclude_unset=True)
            if 'password' in update_data:
                update_data['password'] = self._hash_password(update_data['password'])
            
            update_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Actualizar usuario
            success = self.user_repository.update_one(user_id, update_data)
            if not success:
                return None
            
            # Obtener usuario actualizado
            user = self.user_repository.find_by_id(user_id)
            if user:
                current_app.logger.info(f"Usuario {user_id} actualizado exitosamente")
                return UserResponse(**user)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error actualizando usuario: {e}")
            return None
    
    def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        """
        Cambiar contraseña de usuario
        
        Args:
            user_id: ID del usuario
            password_data: Datos de cambio de contraseña
            
        Returns:
            bool: True si se cambió exitosamente
        """
        try:
            # Obtener usuario
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False
            
            # Verificar contraseña actual
            if not self._verify_password(password_data.current_password, user['password']):
                current_app.logger.warning(f"Contraseña actual incorrecta para usuario {user_id}")
                return False
            
            # Hashear nueva contraseña
            hashed_password = self._hash_password(password_data.new_password)
            
            # Actualizar contraseña
            update_data = {
                'password': hashed_password,
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            success = self.user_repository.update_one(user_id, update_data)
            if success:
                current_app.logger.info(f"Contraseña cambiada exitosamente para usuario {user_id}")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error cambiando contraseña: {e}")
            return False
    
    def has_permission(self, user: UserResponse, required_role: UserRole) -> bool:
        """
        Verificar si usuario tiene permiso
        
        Args:
            user: Usuario a verificar
            required_role: Rol requerido
            
        Returns:
            bool: True si tiene permiso
        """
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.OPERATOR: 2,
            UserRole.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def _hash_password(self, password: str) -> str:
        """Hashear contraseña"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_token(self, user: Dict[str, Any]) -> str:
        """Generar token JWT"""
        payload = {
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(
                hours=current_app.config.get('JWT_EXPIRATION_HOURS', 24)
            )
        }
        
        secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def _decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decodificar token JWT"""
        try:
            secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError:
            current_app.logger.warning("Token inválido")
            return None
    
    def _generate_refresh_token(self) -> str:
        """Generar refresh token seguro"""
        return secrets.token_urlsafe(32)
    
    def _hash_refresh_token(self, token: str) -> str:
        """Hashear refresh token para almacenamiento seguro"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def store_refresh_token(self, user_id: str, refresh_token: str) -> bool:
        """
        Almacenar refresh token hasheado en la base de datos
        
        Args:
            user_id: ID del usuario
            refresh_token: Token de refresh sin hashear
            
        Returns:
            bool: True si se almacenó correctamente
        """
        try:
            hashed_token = self._hash_refresh_token(refresh_token)
            expires_at = datetime.utcnow() + timedelta(
                days=current_app.config.get('REFRESH_TOKEN_EXPIRATION_DAYS', 30)
            )
            
            return self.user_repository.store_refresh_token(
                user_id, hashed_token, expires_at
            )
        except Exception as e:
            current_app.logger.error(f"Error almacenando refresh token: {e}")
            return False
    
    def validate_refresh_token(self, refresh_token: str) -> Optional[UserResponse]:
        """
        Validar refresh token y obtener usuario
        
        Args:
            refresh_token: Token de refresh
            
        Returns:
            Optional[UserResponse]: Usuario si el token es válido
        """
        try:
            hashed_token = self._hash_refresh_token(refresh_token)
            user = self.user_repository.validate_refresh_token(hashed_token)
            
            if user and user.status == 'active':
                current_app.logger.info(f"Refresh token válido para usuario: {user.username}")
                return user
            else:
                current_app.logger.warning("Refresh token inválido o usuario inactivo")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error validando refresh token: {e}")
            return None
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revocar refresh token
        
        Args:
            refresh_token: Token de refresh a revocar
            
        Returns:
            bool: True si se revocó correctamente
        """
        try:
            hashed_token = self._hash_refresh_token(refresh_token)
            return self.user_repository.revoke_refresh_token(hashed_token)
        except Exception as e:
            current_app.logger.error(f"Error revocando refresh token: {e}")
            return False
    
    def refresh_access_token(self, refresh_token: str) -> Optional[RefreshTokenResponse]:
        """
        Generar nuevo access token usando refresh token
        
        Args:
            refresh_token: Token de refresh válido
            
        Returns:
            Optional[RefreshTokenResponse]: Nuevos tokens o None
        """
        try:
            # Validar refresh token
            user = self.validate_refresh_token(refresh_token)
            if not user:
                return None
            
            # Generar nuevos tokens
            new_access_token = self._generate_access_token(user)
            new_refresh_token = self._generate_refresh_token()
            
            # Almacenar nuevo refresh token
            if not self.store_refresh_token(user.id, new_refresh_token):
                current_app.logger.error("Error almacenando nuevo refresh token")
                return None
            
            # Revocar refresh token anterior
            self.revoke_refresh_token(refresh_token)
            
            current_app.logger.info(f"Tokens renovados para usuario: {user.username}")
            
            return RefreshTokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="Bearer",
                expires_in=current_app.config.get('JWT_EXPIRATION_HOURS', 24) * 3600,
                user=user
            )
            
        except Exception as e:
            current_app.logger.error(f"Error renovando tokens: {e}")
            return None
    
    def logout_user(self, refresh_token: str) -> bool:
        """
        Cerrar sesión del usuario revocando refresh token
        
        Args:
            refresh_token: Token de refresh a revocar
            
        Returns:
            bool: True si se cerró sesión correctamente
        """
        try:
            # Revocar refresh token
            success = self.revoke_refresh_token(refresh_token)
            
            if success:
                current_app.logger.info("Usuario cerró sesión exitosamente")
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error cerrando sesión: {e}")
            return False
