"""
Servicio para manejo de alertas y reportes
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from flask import current_app
from http import HTTPStatus

from app.models.alert_model import (
    AlertConfigCreate, AlertConfigUpdate, AlertConfigResponse,
    AlertCreate, AlertUpdate, AlertResponse, AlertStatus, AlertType, AlertPriority,
    ReportRequest, ReportResponse, AlertSummary, LocationStats
)
from app.repositories.alert_repository import AlertRepository
from app.repositories.alert_config_repository import AlertConfigRepository
from app.repositories.report_repository import ReportRepository
from app.models.user_model import UserResponse, UserRole

class AlertService:
    """Servicio para manejo de alertas y reportes"""
    
    def __init__(self, alert_repository: AlertRepository, 
                 alert_config_repository: AlertConfigRepository,
                 report_repository: ReportRepository):
        """
        Inicializar servicio
        
        Args:
            alert_repository: Repository para alertas
            alert_config_repository: Repository para configuración de alertas
            report_repository: Repository para reportes
        """
        self.alert_repository = alert_repository
        self.alert_config_repository = alert_config_repository
        self.report_repository = report_repository
        current_app.logger.info("AlertService inicializado")
    
    def create_alert_config(self, config_data: AlertConfigCreate, 
                           current_user: UserResponse) -> Optional[AlertConfigResponse]:
        """
        Crear configuración de alerta
        
        Args:
            config_data: Datos de configuración
            current_user: Usuario actual
            
        Returns:
            Optional[AlertConfigResponse]: Configuración creada o None
        """
        try:
            # Verificar permisos
            if not self._has_alert_permission(current_user):
                current_app.logger.warning(f"Usuario {current_user.username} no tiene permisos para crear alertas")
                return None
            
            # Verificar si ya existe configuración para esta ubicación y tipo
            existing = self.alert_config_repository.find_by_location_and_type(
                config_data.location, config_data.alert_type
            )
            if existing:
                current_app.logger.warning(f"Ya existe configuración para {config_data.location} - {config_data.alert_type}")
                return None
            
            # Crear configuración
            config_dict = config_data.dict()
            config_dict['created_by'] = current_user.id
            config_dict['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            config_dict['updated_at'] = config_dict['created_at']
            
            config_id = self.alert_config_repository.insert_one(config_dict)
            if not config_id:
                raise Exception("Error creando configuración de alerta")
            
            # Obtener configuración creada
            config = self.alert_config_repository.find_by_id(config_id)
            if config:
                current_app.logger.info(f"Configuración de alerta creada para {config_data.location}")
                return AlertConfigResponse(**config)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creando configuración de alerta: {e}")
            return None
    
    def update_alert_config(self, config_id: str, config_data: AlertConfigUpdate,
                           current_user: UserResponse) -> Optional[AlertConfigResponse]:
        """
        Actualizar configuración de alerta
        
        Args:
            config_id: ID de la configuración
            config_data: Datos a actualizar
            current_user: Usuario actual
            
        Returns:
            Optional[AlertConfigResponse]: Configuración actualizada o None
        """
        try:
            # Verificar permisos
            if not self._has_alert_permission(current_user):
                return None
            
            # Preparar datos de actualización
            update_data = config_data.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Actualizar configuración
            success = self.alert_config_repository.update_one(config_id, update_data)
            if not success:
                return None
            
            # Obtener configuración actualizada
            config = self.alert_config_repository.find_by_id(config_id)
            if config:
                current_app.logger.info(f"Configuración de alerta {config_id} actualizada")
                return AlertConfigResponse(**config)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error actualizando configuración de alerta: {e}")
            return None
    
    def toggle_alert_config(self, config_id: str, enabled: bool,
                           current_user: UserResponse) -> Optional[AlertConfigResponse]:
        """
        Activar/desactivar configuración de alerta
        
        Args:
            config_id: ID de la configuración
            enabled: Si habilitar o deshabilitar
            current_user: Usuario actual
            
        Returns:
            Optional[AlertConfigResponse]: Configuración actualizada o None
        """
        try:
            # Verificar permisos
            if not self._has_alert_permission(current_user):
                return None
            
            update_data = {
                'enabled': enabled,
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            success = self.alert_config_repository.update_one(config_id, update_data)
            if not success:
                return None
            
            # Obtener configuración actualizada
            config = self.alert_config_repository.find_by_id(config_id)
            if config:
                status = "habilitada" if enabled else "deshabilitada"
                current_app.logger.info(f"Alerta {config_id} {status}")
                return AlertConfigResponse(**config)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error cambiando estado de alerta: {e}")
            return None
    
    def get_alert_configs(self, location: Optional[str] = None) -> List[AlertConfigResponse]:
        """
        Obtener configuraciones de alerta
        
        Args:
            location: Filtrar por ubicación
            
        Returns:
            List[AlertConfigResponse]: Lista de configuraciones
        """
        try:
            configs = self.alert_config_repository.find_all(location=location)
            return [AlertConfigResponse(**config) for config in configs]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo configuraciones de alerta: {e}")
            return []
    
    def check_and_create_alert(self, sensor_reading: Dict[str, Any]) -> Optional[AlertResponse]:
        """
        Verificar si una lectura del sensor debe crear una alerta
        
        Args:
            sensor_reading: Lectura del sensor
            
        Returns:
            Optional[AlertResponse]: Alerta creada o None
        """
        try:
            location = sensor_reading.get('location', 'default')
            nivel_agua = sensor_reading.get('nivel_agua', 0)
            estado = sensor_reading.get('estado', 'normal')
            
            # Obtener configuraciones activas para esta ubicación
            configs = self.alert_config_repository.find_active_by_location(location)
            
            for config in configs:
                # Verificar si se debe crear alerta
                if self._should_create_alert(config, nivel_agua, estado):
                    # Verificar cooldown
                    if not self._is_in_cooldown(config, location):
                        alert = self._create_alert(config, sensor_reading)
                        if alert:
                            current_app.logger.info(f"Alerta creada para {location}: {alert.message}")
                            return AlertResponse(**alert)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error verificando alertas: {e}")
            return None
    
    def acknowledge_alert(self, alert_id: str, current_user: UserResponse,
                         notes: Optional[str] = None) -> Optional[AlertResponse]:
        """
        Reconocer una alerta
        
        Args:
            alert_id: ID de la alerta
            current_user: Usuario que reconoce la alerta
            notes: Notas adicionales
            
        Returns:
            Optional[AlertResponse]: Alerta actualizada o None
        """
        try:
            # Verificar permisos
            if not self._has_alert_permission(current_user):
                return None
            
            update_data = {
                'status': AlertStatus.ACKNOWLEDGED,
                'acknowledged_by': current_user.id,
                'acknowledged_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if notes:
                update_data['notes'] = notes
            
            success = self.alert_repository.update_one(alert_id, update_data)
            if not success:
                return None
            
            # Obtener alerta actualizada
            alert = self.alert_repository.find_by_id(alert_id)
            if alert:
                current_app.logger.info(f"Alerta {alert_id} reconocida por {current_user.username}")
                return AlertResponse(**alert)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error reconociendo alerta: {e}")
            return None
    
    def resolve_alert(self, alert_id: str, current_user: UserResponse,
                     notes: Optional[str] = None) -> Optional[AlertResponse]:
        """
        Resolver una alerta
        
        Args:
            alert_id: ID de la alerta
            current_user: Usuario que resuelve la alerta
            notes: Notas adicionales
            
        Returns:
            Optional[AlertResponse]: Alerta actualizada o None
        """
        try:
            # Verificar permisos
            if not self._has_alert_permission(current_user):
                return None
            
            update_data = {
                'status': AlertStatus.RESOLVED,
                'resolved_by': current_user.id,
                'resolved_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if notes:
                update_data['notes'] = notes
            
            success = self.alert_repository.update_one(alert_id, update_data)
            if not success:
                return None
            
            # Obtener alerta actualizada
            alert = self.alert_repository.find_by_id(alert_id)
            if alert:
                current_app.logger.info(f"Alerta {alert_id} resuelta por {current_user.username}")
                return AlertResponse(**alert)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error resolviendo alerta: {e}")
            return None
    
    def get_active_alerts(self, location: Optional[str] = None, 
                         limit: int = 50) -> List[AlertResponse]:
        """
        Obtener alertas activas
        
        Args:
            location: Filtrar por ubicación
            limit: Límite de alertas
            
        Returns:
            List[AlertResponse]: Lista de alertas activas
        """
        try:
            alerts = self.alert_repository.find_active(location=location, limit=limit)
            return [AlertResponse(**alert) for alert in alerts]
        except Exception as e:
            current_app.logger.error(f"Error obteniendo alertas activas: {e}")
            return []
    
    def get_alert_summary(self, location: Optional[str] = None) -> AlertSummary:
        """
        Obtener resumen de alertas
        
        Args:
            location: Filtrar por ubicación
            
        Returns:
            AlertSummary: Resumen de alertas
        """
        try:
            summary_data = self.alert_repository.get_summary(location=location)
            return AlertSummary(**summary_data)
        except Exception as e:
            current_app.logger.error(f"Error obteniendo resumen de alertas: {e}")
            return AlertSummary(
                total_alerts=0,
                active_alerts=0,
                resolved_alerts=0,
                alerts_by_type={},
                alerts_by_priority={},
                average_resolution_time=None
            )
    
    def create_report(self, report_request: ReportRequest,
                     current_user: UserResponse) -> Optional[ReportResponse]:
        """
        Crear reporte
        
        Args:
            report_request: Solicitud de reporte
            current_user: Usuario que solicita el reporte
            
        Returns:
            Optional[ReportResponse]: Reporte creado o None
        """
        try:
            # Verificar permisos
            if not self._has_report_permission(current_user):
                return None
            
            # Crear reporte
            report_dict = report_request.dict()
            report_dict['created_by'] = current_user.id
            report_dict['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_dict['status'] = 'pending'
            
            report_id = self.report_repository.insert_one(report_dict)
            if not report_id:
                raise Exception("Error creando reporte")
            
            # Obtener reporte creado
            report = self.report_repository.find_by_id(report_id)
            if report:
                current_app.logger.info(f"Reporte {report_id} creado por {current_user.username}")
                return ReportResponse(**report)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creando reporte: {e}")
            return None
    
    def get_location_stats(self, location: str) -> Optional[LocationStats]:
        """
        Obtener estadísticas por ubicación
        
        Args:
            location: Ubicación
            
        Returns:
            Optional[LocationStats]: Estadísticas de la ubicación
        """
        try:
            stats_data = self.alert_repository.get_location_stats(location)
            if stats_data:
                return LocationStats(**stats_data)
            return None
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas de ubicación: {e}")
            return None
    
    def _has_alert_permission(self, user: UserResponse) -> bool:
        """Verificar permisos para alertas"""
        return user.role in [UserRole.ADMIN, UserRole.OPERATOR]
    
    def _has_report_permission(self, user: UserResponse) -> bool:
        """Verificar permisos para reportes"""
        return user.role in [UserRole.ADMIN, UserRole.OPERATOR, UserRole.USER]
    
    def _should_create_alert(self, config: Dict[str, Any], nivel_agua: float, 
                           estado: str) -> bool:
        """Verificar si se debe crear alerta"""
        if not config.get('enabled', True):
            return False
        
        alert_type = config.get('alert_type')
        
        # Verificar umbrales
        threshold_min = config.get('threshold_min')
        threshold_max = config.get('threshold_max')
        
        if threshold_min is not None and nivel_agua < threshold_min:
            return True
        
        if threshold_max is not None and nivel_agua > threshold_max:
            return True
        
        # Verificar por estado
        if alert_type == AlertType.INUNDACION and estado == 'inundación':
            return True
        
        if alert_type == AlertType.SEQUIA and estado == 'sequía':
            return True
        
        return False
    
    def _is_in_cooldown(self, config: Dict[str, Any], location: str) -> bool:
        """Verificar si está en período de cooldown"""
        cooldown_minutes = config.get('cooldown_minutes', 30)
        last_alert = self.alert_repository.find_last_alert_by_config(
            config['_id'], location
        )
        
        if not last_alert:
            return False
        
        last_alert_time = datetime.strptime(last_alert['created_at'], "%Y-%m-%d %H:%M:%S")
        cooldown_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        return last_alert_time > cooldown_time
    
    def _create_alert(self, config: Dict[str, Any], 
                     sensor_reading: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crear alerta"""
        try:
            alert_data = {
                'location': config['location'],
                'alert_type': config['alert_type'],
                'status': AlertStatus.ACTIVE,
                'priority': self._determine_priority(config, sensor_reading),
                'message': self._generate_alert_message(config, sensor_reading),
                'nivel_agua': sensor_reading['nivel_agua'],
                'threshold_triggered': self._get_triggered_threshold(config, sensor_reading),
                'sensor_reading_id': sensor_reading['_id'],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            alert_id = self.alert_repository.insert_one(alert_data)
            if alert_id:
                alert_data['_id'] = alert_id
                return alert_data
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creando alerta: {e}")
            return None
    
    def _determine_priority(self, config: Dict[str, Any], 
                          sensor_reading: Dict[str, Any]) -> AlertPriority:
        """Determinar prioridad de la alerta"""
        nivel_agua = sensor_reading['nivel_agua']
        
        if nivel_agua <= 2.0 or nivel_agua >= 15.0:
            return AlertPriority.CRITICAL
        elif nivel_agua <= 3.0 or nivel_agua >= 12.0:
            return AlertPriority.HIGH
        elif nivel_agua <= 4.0 or nivel_agua >= 10.0:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
    
    def _generate_alert_message(self, config: Dict[str, Any], 
                               sensor_reading: Dict[str, Any]) -> str:
        """Generar mensaje de alerta"""
        nivel_agua = sensor_reading['nivel_agua']
        location = config['location']
        alert_type = config['alert_type']
        
        if alert_type == AlertType.INUNDACION:
            return f"ALERTA DE INUNDACIÓN en {location}: Nivel de agua crítico ({nivel_agua}cm)"
        elif alert_type == AlertType.SEQUIA:
            return f"ALERTA DE SEQUÍA en {location}: Nivel de agua bajo ({nivel_agua}cm)"
        else:
            return f"Alerta en {location}: Nivel de agua anormal ({nivel_agua}cm)"
    
    def _get_triggered_threshold(self, config: Dict[str, Any], 
                                sensor_reading: Dict[str, Any]) -> float:
        """Obtener umbral que se activó"""
        nivel_agua = sensor_reading['nivel_agua']
        threshold_min = config.get('threshold_min')
        threshold_max = config.get('threshold_max')
        
        if threshold_min is not None and nivel_agua < threshold_min:
            return threshold_min
        
        if threshold_max is not None and nivel_agua > threshold_max:
            return threshold_max
        
        return nivel_agua
