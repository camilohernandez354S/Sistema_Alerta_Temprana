"""
Cliente HTTP para enviar datos del Arduino al servidor Flask
"""
import requests
import json
import os
from dotenv import load_dotenv

class ArduinoClient:
    def __init__(self):
        # Cargar configuración
        load_dotenv()
        self.base_url = os.getenv('FLASK_SERVER_URL', 'http://localhost:5000')
        
    def send_raw_reading(self, raw_data):
        """
        Enviar lectura cruda del Arduino al servidor
        
        Args:
            raw_data (str): Datos crudos del Arduino (ej: "nivel_agua: 25.5 cm")
            
        Returns:
            dict: Respuesta del servidor
        """
        try:
            # Filtrar mensajes de inicialización del Arduino
            if any(keyword in raw_data for keyword in ['===', 'Sistema inicializado', 'Intervalo', 'Umbral', '========']):
                return {'info': f'Mensaje de inicialización: {raw_data}'}
            
            # Parsear el dato crudo
            if "TIMESTAMP:" in raw_data and "NIVEL:" in raw_data:
                # Formato nuevo: "TIMESTAMP:5016,NIVEL:240.65,ESTADO:Sequía"
                parts = raw_data.split(",")
                nivel_part = None
                for part in parts:
                    if "NIVEL:" in part:
                        nivel_part = part
                        break
                
                if nivel_part:
                    distancia = float(nivel_part.split(":")[1])
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
            
            # Enviar al endpoint de mediciones
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
                
        except ValueError as e:
            return {'error': f'Error parseando datos: {e}'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Error de conexión: {e}'}
        except Exception as e:
            return {'error': f'Error inesperado: {e}'}
