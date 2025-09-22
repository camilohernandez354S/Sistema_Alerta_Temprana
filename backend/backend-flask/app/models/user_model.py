"""
Modelos para usuarios y autenticación
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

class UserRole(str, Enum):
    """Roles de usuario disponibles"""
    ADMIN = "admin"
    USER = "user"
    OPERATOR = "operator"

class UserStatus(str, Enum):
    """Estados de usuario"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserBase(BaseModel):
    """Modelo base para usuarios"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    role: UserRole = Field(default=UserRole.USER, description="Rol del usuario")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Estado del usuario")
    location: Optional[str] = Field(None, description="Ubicación del usuario")
    
    @validator('username')
    def validate_username(cls, v):
        """Validar formato de username"""
        if not v.isalnum():
            raise ValueError("El username debe contener solo letras y números")
        return v.lower()

class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str = Field(..., min_length=6, description="Contraseña")
    
    @validator('password')
    def validate_password(cls, v):
        """Validar fortaleza de contraseña"""
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

class UserUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    location: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(UserBase):
    """Modelo para respuesta de usuario"""
    id: str = Field(..., alias='_id')
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Fecha de última actualización")
    last_login: Optional[str] = Field(None, description="Último login")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class UserLogin(BaseModel):
    """Modelo para login"""
    username: str = Field(..., description="Nombre de usuario o email")
    password: str = Field(..., description="Contraseña")

class TokenResponse(BaseModel):
    """Modelo para respuesta de token"""
    access_token: str = Field(..., description="Token de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: UserResponse = Field(..., description="Información del usuario")

class RefreshTokenResponse(BaseModel):
    """Modelo para respuesta de refresh token"""
    access_token: str = Field(..., description="Nuevo token de acceso")
    refresh_token: str = Field(..., description="Nuevo token de refresh")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: UserResponse = Field(..., description="Información del usuario")

class PasswordChange(BaseModel):
    """Modelo para cambio de contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validar fortaleza de nueva contraseña"""
        if len(v) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")
        return v
