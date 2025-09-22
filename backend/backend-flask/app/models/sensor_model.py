"""
Modelos de datos para sensores
"""
from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime
from typing import Optional
import re
from bson import ObjectId

class SensorDocumentObtenido(BaseModel):
    """Modelo para un documento de sensor en MongoDB"""
    id: str = Field(..., description="ID del documento en MongoDB", alias='_id')
    nivel_agua: float = Field(..., description="nivel_agua medida en centímetros")
    estado: str = Field(..., description="Estado del nivel de agua")
    timestamp: str = Field(..., description="Fecha y hora de la medición")
    
    @validator('id', pre=True, always=True)
    def validate_id(cls, v):
        """Validar que el ID sea un ObjectId válido"""
        # Si es un ObjectId, lo convertimos a string
        if isinstance(v, ObjectId):
            return str(v)
            
        # Si es una string, la validamos
        if not v:
            raise ValueError("El ID no puede ser vacío")
            
        if not ObjectId.is_valid(v):
            raise ValueError("ID no es un ObjectId válido")
        return v

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
                "nivel_agua": 10.5,
                "estado": "normal",
                "timestamp": "2025-05-16 14:45:02"
            }
        }

class SensorReading(BaseModel):
    """Modelo para la lectura cruda del sensor"""
    nivel_agua: str = Field(..., description="Datos brutos recibidos del Arduino")
    
    @validator('nivel_agua')
    def validar_data(cls, v):
        """Validar el formato de los datos crudos del Arduino"""
        # Verificar que el formato sea "nivel_agua: [número]cm" o "Distancia: [número]cm"
        if not re.match(r"^(nivel_agua|Distancia):\s*\d+(?:\.\d+)?\scm$", v):
            raise ValueError("Formato de datos inválido. Debe ser 'nivel_agua: [número]cm' o 'Distancia: [número]cm'")
        return v
    
    def extraer_nivel_agua(self) -> float:
        """Extraer el valor numérico del nivel del agua de la lectura cruda"""
        try:
            # Manejar tanto "nivel_agua:" como "Distancia:"
            nivel_agua_str = self.nivel_agua.replace("nivel_agua:", "").replace("Distancia:", "").replace("cm", "").strip()
            nivel_agua = float(nivel_agua_str)
            return nivel_agua
        except ValueError:
            raise ValueError("No se pudo extraer un número válido del nivel del agua")

class SensorData(BaseModel):
    """Modelo para los datos procesados del sensor"""
    nivel_agua: float = Field(..., description="Nivel de agua medida en centímetros")
    estado: str = Field(..., description="Estado del nivel de agua")
    timestamp: str = Field(..., description="Fecha y hora de la medición")
    
    class Config:
        """Configuración del modelo"""
        json_schema_extra = {
            "example": {
                "nivel_agua": 10.5,
                "estado": "normal",
                "timestamp": "2025-05-16 14:45:02"
            }
        }
    
    @validator('nivel_agua')
    def validate_distance(cls, v):
        """Validar que el nivel del agua esté en un rango razonable"""
        if v < 0:
            raise ValueError("El nivel del agua no puede ser negativa")
        if v > 2000:  # Aumentamos el límite máximo a 2000cm
            raise ValueError("El nivel del agua debe ser menor a 2000cm")
        return v
    
    @validator('estado')
    def validate_estado(cls, v):
        """Validar que el estado sea uno de los valores permitidos"""
        valid_states = ['inundación', 'sequía', 'normal']
        if v not in valid_states:
            raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}")
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validar que el timestamp tenga el formato correcto"""
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError("Formato de timestamp inválido. Debe ser YYYY-MM-DD HH:MM:SS")

class SensorDocumentGuardado(BaseModel):
    """Modelo para el documento que se guardará en MongoDB"""
    nivel_agua: float = Field(..., description="Nivel de agua medida en centímetros")
    estado: str = Field(..., description="Estado del nivel de agua")
    timestamp: str = Field(..., description="Fecha y hora de la medición")
    
    class Config:
        """Configuración del modelo"""
        json_schema_extra = {
            "example": {
                "nivel_agua": 10.5,
                "estado": "normal",
                "timestamp": "2025-05-16 14:45:02"
            }
        }

class SensorDocumentRangoTiempo(SensorDocumentObtenido):
    """Modelo para el documento que se guardará en MongoDB"""
    nivel_agua: float = Field(..., description="Nivel de agua medida en centímetros")
    estado: str = Field(..., description="Estado del nivel de agua")
    timestamp: str = Field(..., description="Fecha y hora de la medición")
    
    class Config:
        """Configuración del modelo"""
        json_schema_extra = {
            "example": {
                "nivel_agua": 10.5,
                "estado": "normal",
                "timestamp": "2025-05-16 14:45:02"
            }
        }

class EstadoSensorStats(BaseModel):
    """Modelo para estadísticas de estados del sensor"""
    sequia: int = Field(..., description="Cantidad de mediciones en estado de sequía")
    normal: int = Field(..., description="Cantidad de mediciones en estado normal")
    inundacion: int = Field(..., description="Cantidad de mediciones en estado de inundación")
    
    @field_validator('sequia', 'normal', 'inundacion', mode='before')
    def normalize_key(cls, v, info):
        """Normaliza los nombres de los campos, convirtiendo de con tilde a sin tilde"""
        if isinstance(v, dict):
            field_name = info.field_name
            return v.get(field_name, v.get(field_name.replace('í', 'i'), 0))
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "sequia": 15,
                "normal": 60,
                "inundacion": 25
            }
        }
