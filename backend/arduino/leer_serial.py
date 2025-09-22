import serial
import time
from dotenv import load_dotenv
import os
from pathlib import Path
from arduino_client import ArduinoClient
import serial.tools.list_ports

env_path = Path(__file__).resolve().parent / "../backend-flask/.env"
load_dotenv(dotenv_path=env_path)

# Cargar configuración
PORT = os.getenv("SERIAL_PORT", "COM5")  # Puerto por defecto COM7
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))

# Inicializar cliente HTTP
arduino_client = ArduinoClient()

# Función para verificar si el puerto está disponible

def verificar_puerto_disponible(port):
    if not port:
        return False
    ports = serial.tools.list_ports.comports()
    return any(p.device == port for p in ports)

try:
    # Verificar si el puerto está disponible
    if not PORT:
        print("❌ Error: No se especificó puerto serial")
        print("💡 Crea un archivo .env en backend/backend-flask/ con SERIAL_PORT=COM7")
        print("Puertos disponibles:")
        for port in serial.tools.list_ports.comports():
            print(f"  - {port.device}")
        exit(1)
        
    if not verificar_puerto_disponible(PORT):
        print(f"❌ Error: El puerto {PORT} no está disponible")
        print("Puertos disponibles:")
        for port in serial.tools.list_ports.comports():
            print(f"  - {port.device}")
        exit(1)

    # Intentar conectar al Arduino
    print(f"📡 Intentando conectar a Arduino en puerto {PORT}")
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
    print(f"✅ Conectado exitosamente a Arduino en puerto {PORT}")
    time.sleep(1)
    
    print("📡 Escuchando datos del Arduino...")

    while True:
        try:
            if arduino.in_waiting:
                nivel_agua = arduino.readline().decode().strip()
                print(f"🔍 Recibido: {nivel_agua}")

                # Enviar datos al servidor usando el endpoint correcto para lecturas crudas
                try:
                    response = arduino_client.send_raw_reading(nivel_agua)
                    
                    if "error" in response:
                        print(f"❌ Error del servidor: {response['error']}")
                    elif "info" in response:
                        print(f"ℹ️  {response['info']}")
                    elif "data" in response:
                        print(f"✅ Datos procesados: {response['data']}")
                    else:
                        print(f"✅ Medición guardada: {response.get('mensaje', 'OK')}")
                except Exception as db_error:
                    print(f"❌ Error al enviar datos a la base de datos: {str(db_error)}")
                    time.sleep(5)  # Esperar antes de intentar nuevamente
                    
        except serial.SerialException as se:
            print(f"❌ Error de puerto serie: {str(se)}")
            print("Reintentando conexión en 5 segundos...")
            time.sleep(5)
            
            # Intentar reconectar
            try:
                arduino.close()
                arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
                print(f"✅ Reconexión exitosa en {PORT}")
            except Exception as reconn_error:
                print(f"❌ No se pudo reconectar: {str(reconn_error)}")
                break
                
        except Exception as e:
            print(f"❌ Error general: {str(e)}")
            time.sleep(1)
            
        time.sleep(1)  # Pequeña pausa para evitar uso excesivo de CPU
            
except serial.SerialException as se:
    print(f"❌ Error inicial al conectar al puerto: {str(se)}")
    print("Verifique:")
    print("1. Que el Arduino esté conectado")
    print("2. Que el puerto no esté ocupado")
    print("3. Que los permisos del puerto estén correctos")
    print("Puertos disponibles:")
    for port in serial.tools.list_ports.comports():
        print(f"  - {port.device}")
    
except Exception as e:
    print(f"❌ Error inesperado al iniciar: {str(e)}")
finally:
    try:
        if 'arduino' in locals() and arduino.is_open:
            arduino.close()
            print("✅ Puerto cerrado correctamente")
    except:
        pass