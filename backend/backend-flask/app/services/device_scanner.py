"""
Servicio para detectar y gestionar dispositivos Arduino conectados
"""
import serial.tools.list_ports
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from bson import ObjectId

from app.models.device import DeviceDocument, DeviceStatus, DeviceCreate
from app.repositories.device_repository import DeviceRepository

logger = logging.getLogger(__name__)


class DeviceScanner:
    """
    Servicio para detectar y gestionar dispositivos Arduino conectados.
    Sigue el principio SRP: responsabilidad única de escaneo de dispositivos.
    """
    
    def __init__(self, device_repository: DeviceRepository):
        """
        Inicializar el escáner de dispositivos
        
        Args:
            device_repository: Repositorio para operaciones de dispositivos
        """
        self.device_repository = device_repository
        self.known_ports = set()
        self._initialize_known_ports()

    def _initialize_known_ports(self):
        """Inicializa la lista de puertos conocidos desde la base de datos."""
        try:
            devices = self.device_repository.find_all()
            self.known_ports = {device.port for device in devices}
            logger.info(f"Puertos conocidos inicializados: {self.known_ports}")
        except Exception as e:
            logger.error(f"Error inicializando puertos conocidos: {e}")
            self.known_ports = set()

    def scan_devices(self) -> Dict[str, int]:
        """
        Escanea puertos disponibles y actualiza el estado de dispositivos.
        Retorna estadísticas del escaneo.
        """
        try:
            # Obtener puertos disponibles
            available_ports = self._get_available_ports()
            current_ports = {port.device for port in available_ports}
            
            # Estadísticas
            stats = {
                'new_devices': 0,
                'reactivated': 0,
                'deactivated': 0,
                'total_active': 0
            }
            
            # Procesar puertos activos
            for port_info in available_ports:
                port = port_info.device
                device = self._get_or_create_device(port, port_info)
                
                if device and device.status == DeviceStatus.INACTIVE:
                    self.device_repository.update_status_by_port(port, DeviceStatus.ACTIVE)
                    stats['reactivated'] += 1
                    logger.info(f"Dispositivo reactivado: {device.name} en {port}")
                elif device:
                    self.device_repository.update_status_by_port(port, DeviceStatus.ACTIVE)
                
                stats['total_active'] += 1
            
            # Marcar como inactivos los dispositivos no conectados
            inactive_devices = self.device_repository.find_by_status(DeviceStatus.ACTIVE)
            
            for device in inactive_devices:
                if device.port not in current_ports:
                    self.device_repository.update_status(device.id, DeviceStatus.INACTIVE)
                    stats['deactivated'] += 1
                    logger.info(f"Dispositivo desactivado: {device.name} en {device.port}")
            
            logger.info(f"Escaneo completado: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error durante el escaneo de dispositivos: {e}")
            return {'error': str(e)}

    def _get_available_ports(self) -> List:
        """Obtiene la lista de puertos seriales disponibles."""
        try:
            ports = serial.tools.list_ports.comports()
            # Filtrar puertos que parecen ser Arduino (USB)
            arduino_ports = [
                port for port in ports 
                if any(keyword in port.description.lower() 
                      for keyword in ['arduino', 'usb', 'serial', 'ch340', 'cp210', 'ftdi'])
            ]
            return arduino_ports
        except Exception as e:
            logger.error(f"Error obteniendo puertos disponibles: {e}")
            return []

    def _get_or_create_device(self, port: str, port_info) -> Optional[DeviceDocument]:
        """Obtiene un dispositivo existente o crea uno nuevo."""
        device = self.device_repository.find_by_port(port)
        
        if not device:
            # Crear nuevo dispositivo
            device_name = self._generate_device_name(port, port_info)
            device_config = self._generate_device_config(port_info)
            
            device_data = DeviceCreate(
                name=device_name,
                port=port,
                config=device_config
            )
            
            device = self.device_repository.create_device(device_data)
            if device:
                logger.info(f"Nuevo dispositivo creado: {device_name} en {port}")
            
        return device

    def _generate_device_name(self, port: str, port_info) -> str:
        """Genera un nombre único para el dispositivo."""
        base_name = f"Arduino_{port.replace('/', '_').replace('\\', '_')}"
        
        # Verificar si el nombre ya existe
        counter = 1
        name = base_name
        while self.device_repository.find_by_port(port) and self.device_repository.find_by_port(port).name == name:
            name = f"{base_name}_{counter}"
            counter += 1
        
        return name

    def _generate_device_config(self, port_info) -> Dict[str, Any]:
        """Genera configuración inicial para el dispositivo."""
        config = {
            'description': port_info.description,
            'hwid': port_info.hwid,
            'vid': port_info.vid,
            'pid': port_info.pid,
            'serial_number': port_info.serial_number,
            'manufacturer': port_info.manufacturer,
            'product': port_info.product,
            'created_at': datetime.utcnow().isoformat()
        }
        return config

    def get_device_status(self) -> List[Dict[str, Any]]:
        """Obtiene el estado actual de todos los dispositivos."""
        try:
            return self.device_repository.get_devices_status()
        except Exception as e:
            logger.error(f"Error obteniendo estado de dispositivos: {e}")
            return []

    def update_device(self, device_id: str, name: str = None, config: Dict[str, Any] = None) -> Optional[DeviceDocument]:
        """Actualiza la información de un dispositivo."""
        try:
            from app.models.device import DeviceUpdate
            
            update_data = DeviceUpdate(
                name=name,
                config=config
            )
            
            device = self.device_repository.update_by_id(device_id, update_data)
            if device:
                logger.info(f"Dispositivo actualizado: {device.name}")
            return device
            
        except Exception as e:
            logger.error(f"Error actualizando dispositivo {device_id}: {e}")
            return None

    def get_device_statistics(self) -> Dict[str, int]:
        """Obtiene estadísticas de dispositivos."""
        try:
            return {
                'total': len(self.device_repository.find_all()),
                'active': self.device_repository.get_active_devices_count(),
                'inactive': self.device_repository.get_inactive_devices_count()
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de dispositivos: {e}")
            return {'total': 0, 'active': 0, 'inactive': 0}
