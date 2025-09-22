"""
Servicio para recuperación de contraseñas
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from flask import current_app
from http import HTTPStatus

from app.models.password_reset_model import (
    PasswordResetRequest, PasswordResetConfirm, PasswordResetResponse,
    PasswordResetStats, PasswordResetCreate
)
from app.models.user_model import UserResponse, UserUpdate
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import email_service

class PasswordResetService:
    """Servicio para manejo de recuperación de contraseñas"""
    
    def __init__(self, reset_repository: PasswordResetRepository, user_repository: UserRepository):
        """
        Inicializar servicio
        
        Args:
            reset_repository: Repository para tokens de reset
            user_repository: Repository para usuarios
        """
        self.reset_repository = reset_repository
        self.user_repository = user_repository
        current_app.logger.info("PasswordResetService inicializado")
    
    def request_password_reset(self, request_data: PasswordResetRequest) -> Dict[str, Any]:
        """
        Solicitar reset de contraseña
        
        Args:
            request_data: Datos de la solicitud
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            email = request_data.email.lower()
            
            # Verificar rate limiting
            if self.reset_repository.is_rate_limited(email, max_requests_per_hour=3):
                return {
                    'success': False,
                    'message': 'Demasiadas solicitudes. Intenta nuevamente en una hora.',
                    'error_code': 'RATE_LIMITED'
                }
            
            # Buscar usuario por email
            user = self.user_repository.find_by_email(email)
            if not user:
                # Por seguridad, devolver éxito incluso si el email no existe
                current_app.logger.warning(f"Intento de reset para email no registrado: {email}")
                return {
                    'success': True,
                    'message': 'Si el email está registrado, recibirás un enlace de recuperación.'
                }
            
            # Invalidar tokens anteriores del usuario
            self.reset_repository.invalidate_user_tokens(user.id)
            
            # Generar token seguro
            token = self._generate_reset_token()
            
            # Crear token de reset
            reset_data = PasswordResetCreate(
                email=email,
                user_id=user.id
            )
            
            token_id = self.reset_repository.create_reset_token(
                reset_data, 
                token, 
                expires_in_hours=1  # Token válido por 1 hora
            )
            
            if not token_id:
                return {
                    'success': False,
                    'message': 'Error creando token de reset'
                }
            
            # Enviar email de recuperación
            reset_url = self._build_reset_url(token)
            
            email_data = {
                'reset_token': token,
                'user_name': user.full_name,
                'reset_url': reset_url,
                'expires_in': '1 hora'
            }
            
            email_sent = email_service.send_notification_email(
                email, 
                'password_reset', 
                email_data
            )
            
            if email_sent:
                current_app.logger.info(f"Email de reset enviado a: {email}")
                return {
                    'success': True,
                    'message': 'Se ha enviado un enlace de recuperación a tu email.',
                    'token_id': token_id
                }
            else:
                current_app.logger.error(f"Error enviando email de reset a: {email}")
                return {
                    'success': False,
                    'message': 'Error enviando email de recuperación'
                }
                
        except Exception as e:
            current_app.logger.error(f"Error en solicitud de reset: {e}")
            return {
                'success': False,
                'message': 'Error interno del servidor'
            }
    
    def confirm_password_reset(self, confirm_data: PasswordResetConfirm) -> Dict[str, Any]:
        """
        Confirmar reset de contraseña
        
        Args:
            confirm_data: Datos de confirmación
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            token = confirm_data.token
            
            # Buscar token de reset
            reset_token = self.reset_repository.find_by_token(token)
            if not reset_token:
                return {
                    'success': False,
                    'message': 'Token de reset inválido o no encontrado',
                    'error_code': 'INVALID_TOKEN'
                }
            
            # Verificar si el token está expirado
            if datetime.utcnow() > reset_token.expires_at:
                # Marcar como expirado
                self.reset_repository.mark_as_expired(token)
                return {
                    'success': False,
                    'message': 'El token de reset ha expirado. Solicita uno nuevo.',
                    'error_code': 'TOKEN_EXPIRED'
                }
            
            # Verificar si ya fue usado
            if reset_token.status != 'pending':
                return {
                    'success': False,
                    'message': 'El token ya ha sido usado',
                    'error_code': 'TOKEN_USED'
                }
            
            # Obtener usuario
            user = self.user_repository.find_by_id(reset_token.user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'Usuario no encontrado',
                    'error_code': 'USER_NOT_FOUND'
                }
            
            # Actualizar contraseña del usuario
            import bcrypt
            password_hash = bcrypt.hashpw(confirm_data.new_password.encode('utf-8'), bcrypt.gensalt())
            
            update_data = UserUpdate(
                password_hash=password_hash.decode('utf-8'),
                updated_at=datetime.utcnow()
            )
            
            success = self.user_repository.update_one(reset_token.user_id, update_data.dict())
            
            if success:
                # Marcar token como usado
                self.reset_repository.mark_as_used(token)
                
                current_app.logger.info(f"Contraseña actualizada para usuario: {user.username}")
                
                return {
                    'success': True,
                    'message': 'Contraseña actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error actualizando contraseña'
                }
                
        except Exception as e:
            current_app.logger.error(f"Error confirmando reset: {e}")
            return {
                'success': False,
                'message': 'Error interno del servidor'
            }
    
    def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """
        Validar token de reset
        
        Args:
            token: Token a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        try:
            reset_token = self.reset_repository.find_by_token(token)
            
            if not reset_token:
                return {
                    'success': False,
                    'message': 'Token inválido',
                    'error_code': 'INVALID_TOKEN'
                }
            
            if datetime.utcnow() > reset_token.expires_at:
                return {
                    'success': False,
                    'message': 'Token expirado',
                    'error_code': 'TOKEN_EXPIRED'
                }
            
            if reset_token.status != 'pending':
                return {
                    'success': False,
                    'message': 'Token ya utilizado',
                    'error_code': 'TOKEN_USED'
                }
            
            return {
                'success': True,
                'message': 'Token válido',
                'user_email': reset_token.email
            }
            
        except Exception as e:
            current_app.logger.error(f"Error validando token: {e}")
            return {
                'success': False,
                'message': 'Error validando token'
            }
    
    def get_reset_stats(self) -> PasswordResetStats:
        """
        Obtener estadísticas de reset
        
        Returns:
            PasswordResetStats: Estadísticas
        """
        try:
            return self.reset_repository.get_reset_stats()
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas: {e}")
            return PasswordResetStats(
                total_requests=0,
                pending_requests=0,
                used_requests=0,
                expired_requests=0,
                today_requests=0
            )
    
    def cleanup_expired_tokens(self) -> int:
        """
        Limpiar tokens expirados
        
        Returns:
            int: Número de tokens eliminados
        """
        try:
            return self.reset_repository.cleanup_expired_tokens()
        except Exception as e:
            current_app.logger.error(f"Error limpiando tokens: {e}")
            return 0
    
    def _generate_reset_token(self) -> str:
        """
        Generar token de reset seguro
        
        Returns:
            str: Token generado
        """
        # Generar token de 32 bytes y convertir a string base64
        token_bytes = secrets.token_bytes(32)
        token = secrets.token_urlsafe(32)
        
        # Agregar timestamp para mayor seguridad
        timestamp = str(int(datetime.utcnow().timestamp()))
        combined = f"{token}_{timestamp}"
        
        # Hashear para almacenamiento
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _build_reset_url(self, token: str) -> str:
        """
        Construir URL de reset
        
        Args:
            token: Token de reset
            
        Returns:
            str: URL completa
        """
        base_url = current_app.config.get('FRONTEND_URL', 'http://localhost:8080')
        return f"{base_url}/reset-password?token={token}"
    
    def get_user_recent_resets(self, user_id: str, limit: int = 5) -> List[PasswordResetResponse]:
        """
        Obtener resets recientes de un usuario
        
        Args:
            user_id: ID del usuario
            limit: Límite de resultados
            
        Returns:
            List[PasswordResetResponse]: Lista de resets
        """
        try:
            return self.reset_repository.find_by_user_id(user_id)[:limit]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo resets recientes: {e}")
            return []
