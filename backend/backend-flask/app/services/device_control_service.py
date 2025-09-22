"""
Servicio para control de dispositivos IoT (Arduino)
Maneja la comunicación para control del buzzer y otros actuadores
"""
import logging
import requests
import serial
import json
import os
import time
from typing import Dict, Optional
from threading import Thread, Lock

# Logger específico para control de dispositivos
device_logger = logging.getLogger('device_control')
device_logger.setLevel(logging.INFO)

class DeviceControlService:
    """Servicio para control de dispositivos IoT"""
    
    def __init__(self):
        # Configuración de comunicación
        self.serial_port = os.getenv('SERIAL_PORT', 'COM11')
        self.baud_rate = int(os.getenv('BAUD_RATE', '9600'))
        self.device_url = os.getenv('IOT_DEVICE_URL', None)  # Para HTTP si está disponible
        
        # Control de conexión serial
        self.serial_connection = None
        self.serial_lock = Lock()
        self.connection_active = False
        
        # Configuración de comandos
        self.commands = {
            'activate_buzzer': 'BUZZER_ON',
            'deactivate_buzzer': 'BUZZER_OFF',
            'set_buzzer_tone': 'BUZZER_TONE',
            'get_status': 'STATUS',
            'reset': 'RESET'
        }
        
        self._init_serial_connection()
    
    def _init_serial_connection(self):
        """Inicializar conexión serial con Arduino"""
        try:
            if self.serial_port and self.serial_port != 'None':
                import serial.tools.list_ports
                
                # Verificar que el puerto esté disponible
                ports = [p.device for p in serial.tools.list_ports.comports()]
                if self.serial_port in ports:
                    self.serial_connection = serial.Serial(
                        self.serial_port, 
                        self.baud_rate, 
                        timeout=2
                    )
                    self.connection_active = True
                    device_logger.info(f"Conexión serial establecida en {self.serial_port}")
                    
                    # Esperar a que Arduino se inicialice
                    time.sleep(2)
                else:
                    device_logger.warning(f"Puerto {self.serial_port} no disponible. Puertos: {ports}")
            else:
                device_logger.info("Puerto serial no configurado, usando modo simulación")
        except Exception as e:
            device_logger.error(f"Error inicializando conexión serial: {e}")
            self.connection_active = False
    
    def send_command_serial(self, command: str, parameters: Dict = None) -> Dict:
        """
        Enviar comando via comunicación serial
        
        Args:
            command: Comando a enviar
            parameters: Parámetros adicionales del comando
            
        Returns:
            dict: Resultado de la operación
        """
        if not self.connection_active or not self.serial_connection:
            return self._simulate_command(command, parameters)
        
        try:
            with self.serial_lock:
                # Construir comando
                cmd_data = {
                    'command': self.commands.get(command, command),
                    'timestamp': int(time.time())
                }
                
                if parameters:
                    cmd_data.update(parameters)
                
                # Enviar comando como JSON
                command_str = json.dumps(cmd_data) + '\n'
                self.serial_connection.write(command_str.encode())
                
                # Esperar respuesta (timeout 3 segundos)
                response = None
                start_time = time.time()
                while time.time() - start_time < 3:
                    if self.serial_connection.in_waiting:
                        response = self.serial_connection.readline().decode().strip()
                        break
                    time.sleep(0.1)
                
                if response:
                    try:
                        result = json.loads(response)
                    except json.JSONDecodeError:
                        result = {'status': 'success', 'message': response}
                else:
                    result = {'status': 'timeout', 'message': 'No se recibió respuesta del dispositivo'}
                
                device_logger.info(f"Comando serial enviado: {command} -> {result}")
                return result
                
        except Exception as e:
            device_logger.error(f"Error enviando comando serial: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def send_command_http(self, command: str, parameters: Dict = None) -> Dict:
        """
        Enviar comando via HTTP (si el dispositivo lo soporta)
        
        Args:
            command: Comando a enviar
            parameters: Parámetros adicionales
            
        Returns:
            dict: Resultado de la operación
        """
        if not self.device_url:
            return {'status': 'error', 'message': 'URL del dispositivo no configurada'}
        
        try:
            payload = {
                'command': command,
                'parameters': parameters or {},
                'timestamp': int(time.time())
            }
            
            response = requests.post(
                f"{self.device_url}/api/command",
                json=payload,
                timeout=5
            )
            
            if response.ok:
                result = response.json()
            else:
                result = {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
            
            device_logger.info(f"Comando HTTP enviado: {command} -> {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            device_logger.error(f"Error enviando comando HTTP: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _simulate_command(self, command: str, parameters: Dict = None) -> Dict:
        """Simular comando cuando no hay conexión real"""
        device_logger.info(f"SIMULACIÓN - Comando: {command}, Parámetros: {parameters}")
        
        # Simular respuestas según el comando
        responses = {
            'activate_buzzer': {
                'status': 'success',
                'message': 'Buzzer activado (simulado)',
                'buzzer_active': True
            },
            'deactivate_buzzer': {
                'status': 'success',
                'message': 'Buzzer desactivado (simulado)',
                'buzzer_active': False
            },
            'set_buzzer_tone': {
                'status': 'success',
                'message': f'Tono configurado: {parameters.get("frequency", 1000)}Hz (simulado)',
                'frequency': parameters.get('frequency', 1000) if parameters else 1000
            },
            'get_status': {
                'status': 'success',
                'device_status': 'online_simulated',
                'buzzer_active': False,
                'last_sensor_reading': 25.5,
                'uptime': 3600
            }
        }
        
        return responses.get(command, {
            'status': 'success',
            'message': f'Comando {command} ejecutado (simulado)'
        })
    
    def activate_buzzer(self, alert_type: str = 'general', frequency: int = None) -> Dict:
        """
        Activar buzzer con configuración específica
        
        Args:
            alert_type: Tipo de alerta ('inundacion', 'sequia', 'general')
            frequency: Frecuencia del tono (Hz)
            
        Returns:
            dict: Resultado de la operación
        """
        # Configurar frecuencia según tipo de alerta
        if not frequency:
            frequencies = {
                'inundacion': 1500,  # Tono agudo para inundación
                'sequia': 400,       # Tono grave para sequía
                'general': 1000      # Tono medio para alertas generales
            }
            frequency = frequencies.get(alert_type, 1000)
        
        parameters = {
            'alert_type': alert_type,
            'frequency': frequency,
            'pattern': 'continuous' if alert_type == 'inundacion' else 'intermittent'
        }
        
        # Intentar primero por serial, luego por HTTP
        result = self.send_command_serial('activate_buzzer', parameters)
        
        if result.get('status') != 'success' and self.device_url:
            result = self.send_command_http('activate_buzzer', parameters)
        
        device_logger.info(f"Buzzer activado - tipo: {alert_type}, frecuencia: {frequency}Hz")
        return result
    
    def deactivate_buzzer(self) -> Dict:
        """
        Desactivar buzzer
        
        Returns:
            dict: Resultado de la operación
        """
        # Intentar por serial primero
        result = self.send_command_serial('deactivate_buzzer')
        
        if result.get('status') != 'success' and self.device_url:
            result = self.send_command_http('deactivate_buzzer')
        
        device_logger.info("Buzzer desactivado")
        return result
    
    def get_device_status(self) -> Dict:
        """
        Obtener estado actual del dispositivo
        
        Returns:
            dict: Estado del dispositivo
        """
        result = self.send_command_serial('get_status')
        
        if result.get('status') != 'success' and self.device_url:
            result = self.send_command_http('get_status')
        
        return result
    
    def test_connection(self) -> Dict:
        """
        Probar la conexión con el dispositivo
        
        Returns:
            dict: Resultado de la prueba
        """
        device_logger.info("Probando conexión con dispositivo...")
        
        # Probar serial
        serial_result = None
        if self.connection_active:
            serial_result = self.send_command_serial('get_status')
        
        # Probar HTTP
        http_result = None
        if self.device_url:
            http_result = self.send_command_http('get_status')
        
        return {
            'serial_connection': {
                'available': self.connection_active,
                'port': self.serial_port,
                'result': serial_result
            },
            'http_connection': {
                'available': bool(self.device_url),
                'url': self.device_url,
                'result': http_result
            },
            'timestamp': int(time.time())
        }
    
    def cleanup(self):
        """Limpiar recursos al cerrar el servicio"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                device_logger.info("Conexión serial cerrada")
            except Exception as e:
                device_logger.error(f"Error cerrando conexión serial: {e}")

# Instancia global del servicio
device_control_service = DeviceControlService()
