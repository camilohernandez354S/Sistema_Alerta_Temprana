"""
Modelos de datos para sensores - Adaptados para datos estructurados del Arduino
"""
from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime
from typing import Optional, List
import re
from bson import ObjectId

# =============================================================================
# NUEVOS MODELOS PARA DATOS ESTRUCTURADOS DEL ARDUINO
# =============================================================================

class LecturaArduinoRequest(BaseModel):
    """
    Modelo para datos estructurados enviados por el Arduino
    
    Estructura JSON esperada:
    {
        "nivel_cm": 45.2,
        "estado": "Normal",
        "intervalo_ms": 5000,
        "velocidad_cm_por_s": 0.02,
        "timestamp": "2025-09-21T15:20:00Z"
    }
    """
    nivel_cm: float = Field(..., description="Nivel de agua en centímetros", ge=0, le=2000)
    estado: str = Field(..., description="Estado del agua clasificado por Arduino")
    intervalo_ms: int = Field(..., description="Intervalo de muestreo en milisegundos", ge=1000, le=300000)
    velocidad_cm_por_s: Optional[float] = Field(None, description="Velocidad de cambio en cm/s", ge=-100, le=100)
    timestamp: Optional[str] = Field(None, description="Timestamp ISO 8601 del Arduino")
    
    @validator('estado')
    def validate_estado(cls, v):
        """Validar que el estado sea uno de los valores permitidos"""
        valid_states = ['Inundación', 'Normal', 'Sequía', 'Error']
        if v not in valid_states:
            raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}")
        return v
    
    @validator('timestamp', pre=True, always=True)
    def validate_timestamp(cls, v):
        """Validar timestamp ISO 8601 o asignar datetime.utcnow() si no se proporciona"""
        if v is None:
            return datetime.utcnow().isoformat() + 'Z'
        
        try:
            # Validar formato ISO 8601
            if isinstance(v, str):
                # Intentar parsear diferentes formatos ISO 8601
                for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S%z']:
                    try:
                        datetime.strptime(v, fmt)
                        return v
                    except ValueError:
                        continue
                raise ValueError("Formato de timestamp inválido")
            return v
        except Exception:
            # Si falla la validación, usar timestamp actual
            return datetime.utcnow().isoformat() + 'Z'
    
    class Config:
        json_schema_extra = {
            "example": {
                "nivel_cm": 45.2,
                "estado": "Normal",
                "intervalo_ms": 5000,
                "velocidad_cm_por_s": 0.02,
                "timestamp": "2025-09-21T15:20:00Z"
            }
        }

class LecturaArduinoResponse(BaseModel):
    """
    Modelo para respuesta de lectura procesada exitosamente
    """
    mensaje: str = Field(..., description="Mensaje de confirmación")
    data: 'LecturaArduinoDocument' = Field(..., description="Datos guardados en MongoDB")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "Lectura procesada exitosamente",
                "data": {
                    "_id": "64b9e2f0e4b0b0b0b0b0b0b0",
                    "nivel_cm": 45.2,
                    "estado": "Normal",
                    "intervalo_ms": 5000,
                    "velocidad_cm_por_s": 0.02,
                    "timestamp": "2025-09-21T15:20:00Z"
                }
            }
        }

class LecturaArduinoDocument(BaseModel):
    """
    Modelo para documento guardado en MongoDB - colección lecturas_sensor
    """
    id: str = Field(..., description="ID del documento en MongoDB", alias='_id')
    nivel_cm: float = Field(..., description="Nivel de agua en centímetros")
    estado: str = Field(..., description="Estado del agua")
    intervalo_ms: int = Field(..., description="Intervalo de muestreo en milisegundos")
    velocidad_cm_por_s: Optional[float] = Field(None, description="Velocidad de cambio en cm/s")
    timestamp: str = Field(..., description="Timestamp ISO 8601")
    
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
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "64b9e2f0e4b0b0b0b0b0b0b0",
                "nivel_cm": 45.2,
                "estado": "Normal",
                "intervalo_ms": 5000,
                "velocidad_cm_por_s": 0.02,
                "timestamp": "2025-09-21T15:20:00Z"
            }
        }

class ConsultaLecturasRequest(BaseModel):
    """
    Modelo para parámetros de consulta de lecturas
    """
    limit: Optional[int] = Field(100, description="Límite de resultados", ge=1, le=1000)
    since: Optional[str] = Field(None, description="Timestamp de inicio (ISO 8601)")
    
    @validator('since')
    def validate_since(cls, v):
        """Validar formato de timestamp since"""
        if v is None:
            return None
        try:
            # Validar formato ISO 8601
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("Formato de timestamp 'since' inválido. Use formato ISO 8601")

# =============================================================================
# MODELOS LEGACY (MANTENER COMPATIBILIDAD)
# =============================================================================

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
        # Verificar formato legacy: "nivel_agua: [número]cm" o "Distancia: [número]cm"
        if re.match(r"^(nivel_agua|Distancia):\s*\d+(?:\.\d+)?\s*cm$", v):
            return v
        
        # Verificar nuevo formato del Arduino: "TIMESTAMP:valor,NIVEL:valor,ESTADO:estado"
        if re.match(r"^TIMESTAMP:\d+,NIVEL:\d+(?:\.\d+)?,ESTADO:(Normal|Sequía|Inundación)$", v):
            return v
            
        raise ValueError("Formato de datos inválido. Formatos soportados: "
                        "'nivel_agua: [número]cm', 'Distancia: [número]cm' o "
                        "'TIMESTAMP:valor,NIVEL:valor,ESTADO:estado'")
    
    def extraer_nivel_agua(self) -> float:
        """Extraer el valor numérico del nivel del agua de la lectura cruda"""
        try:
            # Formato nuevo del Arduino: TIMESTAMP:15002,NIVEL:5.95,ESTADO:Inundación
            if "TIMESTAMP:" in self.nivel_agua and "NIVEL:" in self.nivel_agua:
                return self._parsear_formato_arduino()
            
            # Formato legacy: "nivel_agua: 10.5cm" o "Distancia: 10.5cm"
            else:
                return self._parsear_formato_legacy()
                
        except ValueError as e:
            raise ValueError(f"No se pudo extraer un número válido del nivel del agua: {str(e)}")
    
    def _parsear_formato_arduino(self) -> float:
        """Parsear formato nuevo del Arduino: TIMESTAMP:valor,NIVEL:valor,ESTADO:estado"""
        try:
            # Dividir por comas y buscar el campo NIVEL
            partes = self.nivel_agua.split(',')
            for parte in partes:
                if parte.startswith('NIVEL:'):
                    nivel_str = parte.replace('NIVEL:', '').strip()
                    return float(nivel_str)
            
            raise ValueError("No se encontró el campo NIVEL en los datos")
        except (ValueError, IndexError) as e:
            raise ValueError(f"Error parseando formato Arduino: {str(e)}")
    
    def _parsear_formato_legacy(self) -> float:
        """Parsear formato legacy: nivel_agua: 10.5cm o Distancia: 10.5cm"""
        try:
            # Manejar tanto "nivel_agua:" como "Distancia:"
            nivel_agua_str = self.nivel_agua.replace("nivel_agua:", "").replace("Distancia:", "").replace("cm", "").strip()
            return float(nivel_agua_str)
        except ValueError as e:
            raise ValueError(f"Error parseando formato legacy: {str(e)}")
    
    def extraer_estado_arduino(self) -> Optional[str]:
        """Extraer el estado del formato nuevo del Arduino"""
        try:
            if "TIMESTAMP:" in self.nivel_agua and "ESTADO:" in self.nivel_agua:
                partes = self.nivel_agua.split(',')
                for parte in partes:
                    if parte.startswith('ESTADO:'):
                        estado = parte.replace('ESTADO:', '').strip()
                        # Mapear estados del Arduino a estados del sistema
                        estado_map = {
                            'Normal': 'normal',
                            'Sequía': 'sequía', 
                            'Inundación': 'inundación'
                        }
                        return estado_map.get(estado, 'desconocido')
            return None
        except Exception:
            return None
    
    def extraer_timestamp_arduino(self) -> Optional[int]:
        """Extraer el timestamp del formato nuevo del Arduino"""
        try:
            if "TIMESTAMP:" in self.nivel_agua:
                partes = self.nivel_agua.split(',')
                for parte in partes:
                    if parte.startswith('TIMESTAMP:'):
                        timestamp_str = parte.replace('TIMESTAMP:', '').strip()
                        return int(timestamp_str)
            return None
        except Exception:
            return None

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
