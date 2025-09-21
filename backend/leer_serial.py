import serial
import time
import requests
import re

# Cambia el puerto según tu sistema (ejemplo: 'COM3' en Windows, '/dev/ttyACM0' en Linux)
PUERTO = 'COM5'
BAUDIOS = 9600
BACKEND_URL = 'http://127.0.0.1:5000/api/mediciones'

# Expresión regular para extraer el número de la distancia
PATRON_DISTANCIA = re.compile(r'Distancia:\s*(\d+)')

def main():
    try:
        arduino = serial.Serial(PUERTO, BAUDIOS, timeout=1)
        print(f"Conectado a {PUERTO} a {BAUDIOS} baudios.")
        time.sleep(2)  # Espera a que el Arduino reinicie

        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8', errors='ignore').strip()
                print(f"Dato recibido: {linea}")
                match = PATRON_DISTANCIA.search(linea)
                if match:
                    distancia = int(match.group(1))
                    # Enviar al backend
                    try:
                        response = requests.post(BACKEND_URL, json={"distancia": distancia})
                        if response.status_code == 201:
                            print(f"Enviado al backend: {distancia} cm")
                        else:
                            print(f"Error al enviar al backend: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"Error de conexión al backend: {e}")
            time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
