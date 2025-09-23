"""
Servicio para comunicación con dispositivos Arduino
Integrado en el backend Flask para manejo centralizado
"""
import requests
import json
import os
from pathlib import Path
from flask import current_app
from dotenv import load_dotenv

class ArduinoClientService:
    def __init__(self):
        # Cargar configuración desde el .env del backend-flask
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        
        # Configurar URL base - si no está definida, usar localhost
        self.base_url = os.getenv('FLASK_SERVER_URL', 'http://localhost:5000')
        
        # Log de inicialización
        if current_app:
            current_app.logger.info(f"ArduinoClientService inicializado con URL: {self.base_url}")
        
    def send_raw_reading(self, raw_data):
        """
        Enviar lectura cruda del Arduino al servidor
        Soporta múltiples formatos incluyendo el nuevo formato ESP8266
        
        Args:
            raw_data (str): Datos crudos del Arduino (ej: "nivel_agua: 25.5 cm" o formato JSON)
            
        Returns:
            dict: Respuesta del servidor
        """
        try:
            # Filtrar mensajes de inicialización del Arduino
            if any(keyword in raw_data for keyword in ['===', 'Sistema inicializado', 'Intervalo', 'Umbral', '========']):
                return {'info': f'Mensaje de inicialización: {raw_data}'}
            
            # Intentar parsear como JSON primero (formato ESP8266)
            if raw_data.strip().startswith('{') and raw_data.strip().endswith('}'):
                try:
                    json_data = json.loads(raw_data)
                    # Enviar directamente el JSON al endpoint
                    response = requests.post(
                        f'{self.base_url}/api/mediciones',
                        json=json_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        return response.json()
                    else:
                        return {'error': f'Error del servidor: {response.status_code}'}
                except json.JSONDecodeError:
                    # Si no es JSON válido, continuar con el parsing normal
                    pass
            
            # Parsear el dato crudo (formatos legacy)
            distancia = None
            
            if "TIMESTAMP:" in raw_data and "NIVEL:" in raw_data:
                # Formato nuevo: "TIMESTAMP:5016,NIVEL:240.65,ESTADO:Sequía"
                parts = raw_data.split(",")
                nivel_part = None
                timestamp_part = None
                estado_part = None
                
                for part in parts:
                    if "NIVEL:" in part:
                        nivel_part = part
                    elif "TIMESTAMP:" in part:
                        timestamp_part = part
                    elif "ESTADO:" in part:
                        estado_part = part
                
                if nivel_part:
                    distancia = float(nivel_part.split(":")[1])
                    
                    # Construir JSON para el endpoint
                    payload = {"NIVEL": distancia}
                    if timestamp_part:
                        payload["TIMESTAMP"] = int(timestamp_part.split(":")[1])
                    if estado_part:
                        payload["ESTADO"] = estado_part.split(":")[1]
                        
                    response = requests.post(
                        f'{self.base_url}/api/mediciones',
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        return response.json()
                    else:
                        return {'error': f'Error del servidor: {response.status_code}'}
                else:
                    raise ValueError("No se encontró NIVEL en los datos")
                    
            elif "nivel_agua:" in raw_data:
                # Formato: "nivel_agua: 25.5 cm"
                parts = raw_data.split(":")
                if len(parts) >= 2:
                    value_str = parts[1].strip().replace("cm", "").strip()
                    distancia = float(value_str)
                else:
                    raise ValueError("Formato de datos inválido")
            elif "Distancia:" in raw_data:
                # Formato alternativo: "Distancia: 25.5 cm"
                parts = raw_data.split(":")
                if len(parts) >= 2:
                    value_str = parts[1].strip().replace("cm", "").strip()
                    distancia = float(value_str)
                else:
                    raise ValueError("Formato de datos inválido")
            else:
                # Intentar parsear como número directo
                distancia = float(raw_data.strip())
            
            # Enviar formato legacy al endpoint
            if distancia is not None:
                response = requests.post(
                    f'{self.base_url}/api/mediciones',
                    json={'distancia': distancia},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    return {'error': f'Error del servidor: {response.status_code}'}
            else:
                raise ValueError("No se pudo extraer distancia de los datos")
                
        except ValueError as e:
            error_msg = f'Error parseando datos: {e}'
            if current_app:
                current_app.logger.error(error_msg)
            return {'error': error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f'Error de conexión: {e}'
            if current_app:
                current_app.logger.error(error_msg)
            return {'error': error_msg}
        except Exception as e:
            error_msg = f'Error inesperado: {e}'
            if current_app:
                current_app.logger.error(error_msg)
            return {'error': error_msg}

    def send_measurement_direct(self, distancia, estado=None, timestamp=None):
        """
        Enviar medición directamente sin parsing de texto
        
        Args:
            distancia (float): Valor de distancia en cm
            estado (str, optional): Estado precalculado
            timestamp (int, optional): Timestamp del dispositivo
            
        Returns:
            dict: Respuesta del servidor
        """
        try:
            payload = {"distancia": distancia}
            
            # Si se proporciona estado y timestamp, usar formato ESP8266
            if estado is not None and timestamp is not None:
                payload = {
                    "NIVEL": distancia,
                    "ESTADO": estado,
                    "TIMESTAMP": timestamp
                }
            
            response = requests.post(
                f'{self.base_url}/api/mediciones',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                return {'error': f'Error del servidor: {response.status_code}'}
                
        except Exception as e:
            error_msg = f'Error enviando medición directa: {e}'
            if current_app:
                current_app.logger.error(error_msg)
            return {'error': error_msg}

# Instancia global del servicio
arduino_client_service = ArduinoClientService()
