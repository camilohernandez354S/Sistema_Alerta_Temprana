"""
Modelos para alertas y reportes
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

class AlertType(str, Enum):
    """Tipos de alerta"""
    INUNDACION = "inundacion"
    SEQUIA = "sequia"
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class AlertStatus(str, Enum):
    """Estados de alerta"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISABLED = "disabled"

class AlertPriority(str, Enum):
    """Prioridades de alerta"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertConfig(BaseModel):
    """Configuración de alertas por ubicación"""
    location: str = Field(..., description="Ubicación de la alerta")
    alert_type: AlertType = Field(..., description="Tipo de alerta")
    enabled: bool = Field(default=True, description="Si la alerta está habilitada")
    threshold_min: Optional[float] = Field(None, description="Umbral mínimo")
    threshold_max: Optional[float] = Field(None, description="Umbral máximo")
    notification_email: Optional[str] = Field(None, description="Email para notificaciones")
    notification_sms: Optional[str] = Field(None, description="SMS para notificaciones")
    auto_resolve: bool = Field(default=False, description="Auto-resolver cuando vuelve a normal")
    cooldown_minutes: int = Field(default=30, description="Tiempo de espera entre alertas (minutos)")
    
    @validator('threshold_min', 'threshold_max')
    def validate_thresholds(cls, v):
        """Validar umbrales"""
        if v is not None and v < 0:
            raise ValueError("Los umbrales deben ser positivos")
        return v

class AlertConfigCreate(AlertConfig):
    """Modelo para crear configuración de alerta"""
    pass

class AlertConfigUpdate(BaseModel):
    """Modelo para actualizar configuración de alerta"""
    enabled: Optional[bool] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    notification_email: Optional[str] = None
    notification_sms: Optional[str] = None
    auto_resolve: Optional[bool] = None
    cooldown_minutes: Optional[int] = None

class AlertConfigResponse(AlertConfig):
    """Modelo para respuesta de configuración de alerta"""
    id: str = Field(..., alias='_id')
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Fecha de última actualización")
    created_by: str = Field(..., description="Usuario que creó la configuración")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Alert(BaseModel):
    """Modelo para alertas activas"""
    location: str = Field(..., description="Ubicación de la alerta")
    alert_type: AlertType = Field(..., description="Tipo de alerta")
    status: AlertStatus = Field(default=AlertStatus.ACTIVE, description="Estado de la alerta")
    priority: AlertPriority = Field(..., description="Prioridad de la alerta")
    message: str = Field(..., description="Mensaje de la alerta")
    nivel_agua: float = Field(..., description="Nivel de agua que disparó la alerta")
    threshold_triggered: float = Field(..., description="Umbral que se activó")
    sensor_reading_id: str = Field(..., description="ID de la lectura del sensor")
    acknowledged_by: Optional[str] = Field(None, description="Usuario que reconoció la alerta")
    resolved_by: Optional[str] = Field(None, description="Usuario que resolvió la alerta")
    acknowledged_at: Optional[str] = Field(None, description="Fecha de reconocimiento")
    resolved_at: Optional[str] = Field(None, description="Fecha de resolución")
    notes: Optional[str] = Field(None, description="Notas adicionales")

class AlertCreate(Alert):
    """Modelo para crear alerta"""
    pass

class AlertUpdate(BaseModel):
    """Modelo para actualizar alerta"""
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None

class AlertResponse(Alert):
    """Modelo para respuesta de alerta"""
    id: str = Field(..., alias='_id')
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Fecha de última actualización")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ReportType(str, Enum):
    """Tipos de reporte"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class ReportFormat(str, Enum):
    """Formatos de reporte"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

class ReportRequest(BaseModel):
    """Modelo para solicitar reporte"""
    report_type: ReportType = Field(..., description="Tipo de reporte")
    format: ReportFormat = Field(default=ReportFormat.PDF, description="Formato del reporte")
    location: Optional[str] = Field(None, description="Ubicación específica")
    start_date: Optional[str] = Field(None, description="Fecha de inicio (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Fecha de fin (YYYY-MM-DD)")
    include_alerts: bool = Field(default=True, description="Incluir alertas en el reporte")
    include_predictions: bool = Field(default=True, description="Incluir predicciones en el reporte")
    include_statistics: bool = Field(default=True, description="Incluir estadísticas en el reporte")

class ReportResponse(BaseModel):
    """Modelo para respuesta de reporte"""
    id: str = Field(..., alias='_id')
    report_type: ReportType = Field(..., description="Tipo de reporte")
    format: ReportFormat = Field(..., description="Formato del reporte")
    location: Optional[str] = Field(None, description="Ubicación del reporte")
    start_date: Optional[str] = Field(None, description="Fecha de inicio")
    end_date: Optional[str] = Field(None, description="Fecha de fin")
    file_url: Optional[str] = Field(None, description="URL del archivo generado")
    status: str = Field(..., description="Estado del reporte")
    created_by: str = Field(..., description="Usuario que solicitó el reporte")
    created_at: str = Field(..., description="Fecha de creación")
    completed_at: Optional[str] = Field(None, description="Fecha de completado")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class AlertSummary(BaseModel):
    """Resumen de alertas para reportes"""
    total_alerts: int = Field(..., description="Total de alertas")
    active_alerts: int = Field(..., description="Alertas activas")
    resolved_alerts: int = Field(..., description="Alertas resueltas")
    alerts_by_type: Dict[str, int] = Field(..., description="Alertas por tipo")
    alerts_by_priority: Dict[str, int] = Field(..., description="Alertas por prioridad")
    average_resolution_time: Optional[float] = Field(None, description="Tiempo promedio de resolución (horas)")

class LocationStats(BaseModel):
    """Estadísticas por ubicación"""
    location: str = Field(..., description="Ubicación")
    total_readings: int = Field(..., description="Total de lecturas")
    average_level: float = Field(..., description="Nivel promedio")
    max_level: float = Field(..., description="Nivel máximo")
    min_level: float = Field(..., description="Nivel mínimo")
    alert_count: int = Field(..., description="Cantidad de alertas")
    last_reading: Optional[str] = Field(None, description="Última lectura")
    status: str = Field(..., description="Estado actual")
