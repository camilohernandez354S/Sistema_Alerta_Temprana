"""
Modelos de datos para dispositivos Arduino
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from enum import Enum


class DeviceStatus(str, Enum):
    """Estados posibles de un dispositivo"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class DeviceDocument(BaseModel):
    """Modelo para un documento de dispositivo en MongoDB"""
    id: str = Field(..., description="ID del documento en MongoDB", alias='_id')
    name: str = Field(..., description="Nombre del dispositivo")
    port: str = Field(..., description="Puerto serial del dispositivo")
    status: DeviceStatus = Field(..., description="Estado del dispositivo")
    last_seen: Optional[str] = Field(None, description="Última vez que se vio el dispositivo")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuración del dispositivo")
    created_at: str = Field(..., description="Fecha de creación del dispositivo")
    updated_at: str = Field(..., description="Fecha de última actualización")

    @validator('id', pre=True, always=True)
    def validate_id(cls, v):
        """Validar que el ID sea un ObjectId válido"""
        if isinstance(v, ObjectId):
            return str(v)
        if not v:
            raise ValueError("El ID no puede ser vacío")
        if not ObjectId.is_valid(v):
            raise ValueError("ID no es un ObjectId válido")
        return v

    @validator('name')
    def validate_name(cls, v):
        """Validar que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError("El nombre del dispositivo no puede estar vacío")
        return v.strip()

    @validator('port')
    def validate_port(cls, v):
        """Validar que el puerto no esté vacío"""
        if not v or not v.strip():
            raise ValueError("El puerto no puede estar vacío")
        return v.strip()

    class Config:
        """Configuración del modelo"""
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "64b9e2f0e4b0b0b0b0b0b0b0",
                "name": "Arduino_1",
                "port": "COM3",
                "status": "ACTIVE",
                "last_seen": "2025-01-16T14:45:02Z",
                "config": {
                    "description": "Arduino Uno",
                    "baudrate": 9600
                },
                "created_at": "2025-01-16T14:45:02Z",
                "updated_at": "2025-01-16T14:45:02Z"
            }
        }


class DeviceCreate(BaseModel):
    """Modelo para crear un nuevo dispositivo"""
    name: str = Field(..., description="Nombre del dispositivo")
    port: str = Field(..., description="Puerto serial del dispositivo")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuración del dispositivo")

    @validator('name')
    def validate_name(cls, v):
        """Validar que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError("El nombre del dispositivo no puede estar vacío")
        return v.strip()

    @validator('port')
    def validate_port(cls, v):
        """Validar que el puerto no esté vacío"""
        if not v or not v.strip():
            raise ValueError("El puerto no puede estar vacío")
        return v.strip()


class DeviceUpdate(BaseModel):
    """Modelo para actualizar un dispositivo existente"""
    name: Optional[str] = Field(None, description="Nuevo nombre del dispositivo")
    config: Optional[Dict[str, Any]] = Field(None, description="Nueva configuración del dispositivo")

    @validator('name')
    def validate_name(cls, v):
        """Validar que el nombre no esté vacío si se proporciona"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("El nombre del dispositivo no puede estar vacío")
        return v.strip() if v else v


class DeviceDocumentGuardado(BaseModel):
    """Modelo para el documento que se guardará en MongoDB"""
    name: str = Field(..., description="Nombre del dispositivo")
    port: str = Field(..., description="Puerto serial del dispositivo")
    status: DeviceStatus = Field(..., description="Estado del dispositivo")
    last_seen: Optional[str] = Field(None, description="Última vez que se vio el dispositivo")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuración del dispositivo")
    created_at: str = Field(..., description="Fecha de creación del dispositivo")
    updated_at: str = Field(..., description="Fecha de última actualización")

    class Config:
        """Configuración del modelo"""
        json_schema_extra = {
            "example": {
                "name": "Arduino_1",
                "port": "COM3",
                "status": "ACTIVE",
                "last_seen": "2025-01-16T14:45:02Z",
                "config": {
                    "description": "Arduino Uno",
                    "baudrate": 9600
                },
                "created_at": "2025-01-16T14:45:02Z",
                "updated_at": "2025-01-16T14:45:02Z"
            }
        }
