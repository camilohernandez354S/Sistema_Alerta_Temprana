import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import time

class ArduinoClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        """Inicializar el cliente HTTP"""
        self.base_url = base_url
        self.retry_count = 0
        self.max_retries = 3
        
    def send_sensor_reading(self, nivel_agua: str) -> dict:
        """
        Enviar una lectura del sensor al servidor
        
        Args:
            nivel_agua: Datos brutos del Arduino (ej: "nivel_agua: 10.5cm")
            
        Returns:
            dict: Respuesta del servidor
        """
        try:
            url = f"{self.base_url}/api/sensor/lectura"
            data = {"nivel_agua": nivel_agua}
            
            try:
                response = requests.post(
                    url,
                    json=data,
                    timeout=5,  # Timeout de 5 segundos
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()  # Lanzar excepción si hay error
                
                return response.json()
                
            except ConnectionError as ce:
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    print(f"❌ Error de conexión. Intento {self.retry_count}/{self.max_retries}")
                    time.sleep(2 ** self.retry_count)  # Espera exponencial
                    return self.send_sensor_reading(nivel_agua)  # Intentar nuevamente
                else:
                    print(f"❌ Error de conexión persistente: {str(ce)}")
                    return {"error": "Error de conexión persistente", "details": str(ce)}
                    
            except Timeout as te:
                print(f"❌ Timeout al conectar al servidor: {str(te)}")
                return {"error": "Timeout", "details": str(te)}
                
            except RequestException as re:
                print(f"❌ Error HTTP: {str(re)}")
                return {"error": "Error HTTP", "details": str(re)}
                
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            return {"error": "Error inesperado", "details": str(e)}
            
        finally:
            self.retry_count = 0  # Resetear contador de reintentos

    def send_raw_reading(self, raw_data: str) -> dict:
        """
        Enviar una lectura cruda del sensor al servidor
        
        Args:
            raw_data: Datos brutos del Arduino (ej: "nivel_agua: 10.5cm")
            
        Returns:
            dict: Respuesta del servidor
        """
        try:
            url = f"{self.base_url}/api/sensor/lecturas"
            data = [{"raw_data": raw_data}]
            
            try:
                response = requests.post(
                    url,
                    json=data,
                    timeout=5,  # Timeout de 5 segundos
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()  # Lanzar excepción si hay error
                
                return response.json()
                
            except ConnectionError as ce:
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    print(f"❌ Error de conexión. Intento {self.retry_count}/{self.max_retries}")
                    time.sleep(2 ** self.retry_count)  # Espera exponencial
                    return self.send_raw_reading(raw_data)  # Intentar nuevamente
                else:
                    print(f"❌ Error de conexión persistente: {str(ce)}")
                    return {"error": "Error de conexión persistente", "details": str(ce)}
                    
            except Timeout as te:
                print(f"❌ Timeout al conectar al servidor: {str(te)}")
                return {"error": "Timeout", "details": str(te)}
                
            except RequestException as re:
                print(f"❌ Error HTTP: {str(re)}")
                return {"error": "Error HTTP", "details": str(re)}
                
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            return {"error": "Error inesperado", "details": str(e)}
            
        finally:
            self.retry_count = 0  # Resetear contador de reintentos