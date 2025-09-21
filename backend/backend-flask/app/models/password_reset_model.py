"""
Modelos para recuperación de contraseñas
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class PasswordResetStatus(str, Enum):
    """Estados del token de reset"""
    PENDING = "pending"
    USED = "used"
    EXPIRED = "expired"

class PasswordResetCreate(BaseModel):
    """Modelo para crear token de reset"""
    email: EmailStr = Field(..., description="Email del usuario")
    user_id: str = Field(..., description="ID del usuario")

class PasswordResetResponse(BaseModel):
    """Modelo para respuesta de token de reset"""
    id: str = Field(..., description="ID del token")
    user_id: str = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    token: str = Field(..., description="Token de reset")
    status: PasswordResetStatus = Field(..., description="Estado del token")
    created_at: datetime = Field(..., description="Fecha de creación")
    expires_at: datetime = Field(..., description="Fecha de expiración")
    used_at: Optional[datetime] = Field(None, description="Fecha de uso")

class PasswordResetRequest(BaseModel):
    """Modelo para solicitar reset de contraseña"""
    email: EmailStr = Field(..., description="Email del usuario")
    
    @validator('email')
    def validate_email(cls, v):
        """Validar formato de email"""
        return v.lower().strip()

class PasswordResetConfirm(BaseModel):
    """Modelo para confirmar reset de contraseña"""
    token: str = Field(..., min_length=32, description="Token de reset")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    confirm_password: str = Field(..., min_length=6, description="Confirmación de contraseña")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validar que las contraseñas coincidan"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validar fortaleza de contraseña"""
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        
        # Verificar que tenga al menos una letra y un número
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_letter and has_digit):
            raise ValueError('La contraseña debe contener al menos una letra y un número')
        
        return v

class PasswordResetStats(BaseModel):
    """Modelo para estadísticas de reset"""
    total_requests: int = Field(..., description="Total de solicitudes")
    pending_requests: int = Field(..., description="Solicitudes pendientes")
    used_requests: int = Field(..., description="Solicitudes usadas")
    expired_requests: int = Field(..., description="Solicitudes expiradas")
    today_requests: int = Field(..., description="Solicitudes de hoy")
