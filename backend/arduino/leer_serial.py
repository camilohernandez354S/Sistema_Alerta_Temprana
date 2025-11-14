"""
Sistema de Alerta Temprana - Lector Serial para Arduino Mega
Configurado EXCLUSIVAMENTE para COM5 a 115200 baudios
"""

import serial
import serial.tools.list_ports
import time
import sys
from pathlib import Path

# ============================================================================
# ⚠️ CONFIGURACIÓN FIJA - SOLO COM5 - NO MODIFICAR ⚠️
# ============================================================================
SERIAL_PORT = "COM5"      # ⚠️ FIJO - NO CAMBIAR (Arduino Mega)
SERIAL_BAUDRATE = 9600    # ⚠️ FIJO - 9600 baudios (según nivel_agua.ino)
TIMEOUT_CONEXION = 1
DELAY_RECONEXION = 5
DELAY_LECTURA = 0.1
# ============================================================================

# Agregar backend-flask al path
# En Docker, backend-flask está en el mismo nivel que el código arduino (/app/backend-flask)
# En desarrollo local, está en ../backend-flask
backend_flask_path = Path("/app/backend-flask")
if not backend_flask_path.exists():
    # Fallback para desarrollo local
    backend_flask_path = Path(__file__).resolve().parent / "../backend-flask"
sys.path.append(str(backend_flask_path))

# Importar servicio (opcional)
try:
    from app.services.arduino_client_service import arduino_client_service
except ImportError:
    arduino_client_service = None

def verificar_com5_disponible():
    """Verifica si COM5 está disponible"""
    puertos = serial.tools.list_ports.comports()
    return any(p.device == SERIAL_PORT for p in puertos)

def conectar_com5():
    """Conecta a COM5"""
    try:
        conexion = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            timeout=TIMEOUT_CONEXION
        )
        time.sleep(0.5)
        if conexion.in_waiting:
            conexion.read(conexion.in_waiting)
        return conexion
    except Exception as e:
        print(f"❌ Error conectando a {SERIAL_PORT}: {e}")
        return None

def leer_datos(conexion):
    """Lee línea completa del serial"""
    if not conexion or not conexion.is_open or conexion.in_waiting == 0:
        return None
    try:
        linea = conexion.readline().decode('utf-8', errors='ignore').strip()
        return linea if linea else None
    except:
        return None

def procesar_datos(datos):
    """Procesa datos recibidos del Arduino Mega"""
    if not datos:
        return
    
    # Ignorar mensajes de inicialización
    if any(keyword in datos for keyword in ['===', 'Sistema inicializado', 'Intervalo', 'Umbral', '========']):
        print(f"ℹ️  Mensaje del sistema: {datos[:50]}...")
        return
    
    print(f"📊 Datos recibidos desde {SERIAL_PORT}: {datos}")
    
    # Parsear formato del Arduino: TIMESTAMP:...,NIVEL:...,ESTADO:...
    if "TIMESTAMP:" in datos and "NIVEL:" in datos:
        try:
            partes = datos.split(",")
            nivel = None
            timestamp = None
            estado = None
            
            for parte in partes:
                parte = parte.strip()
                if "NIVEL:" in parte:
                    nivel = float(parte.split(":")[1])
                elif "TIMESTAMP:" in parte:
                    timestamp = parte.split(":")[1]
                elif "ESTADO:" in parte:
                    estado = parte.split(":")[1]
            
            if nivel is not None:
                print(f"   → Nivel de agua: {nivel:.2f} cm")
                if estado:
                    print(f"   → Estado: {estado}")
                if timestamp:
                    print(f"   → Timestamp: {timestamp}")
            
        except Exception as e:
            print(f"   ⚠️ Error parseando datos: {e}")
            print(f"   → Mensaje completo: {datos}")
    # Si es solo un número (distancia directa)
    elif datos.replace('.', '').replace('-', '').isdigit():
        try:
            distancia = float(datos)
            print(f"   → Distancia: {distancia:.2f} cm")
        except ValueError:
            print(f"   → Mensaje: {datos}")
    else:
        print(f"   → Mensaje: {datos}")
    
    # Enviar al servidor Flask si está disponible
    if arduino_client_service:
        try:
            response = arduino_client_service.send_raw_reading(datos)
            if "error" in response:
                print(f"   ❌ Error del servidor: {response['error']}")
            elif "info" in response:
                print(f"   ℹ️  {response['info']}")
            else:
                print(f"   ✅ Datos enviados al servidor Flask")
        except Exception as e:
            print(f"   ⚠️ Error enviando al servidor: {str(e)}")

def main():
    print("=" * 60)
    print("Sistema de Alerta Temprana - Lector Serial Arduino Mega")
    print("=" * 60)
    print(f"🔧 Configuración:")
    print(f"   Puerto: {SERIAL_PORT} (EXCLUSIVO - NO CAMBIAR)")
    print(f"   Velocidad: {SERIAL_BAUDRATE} baudios")
    print(f"   Formato esperado: TIMESTAMP:...,NIVEL:...,ESTADO:...")
    print("=" * 60)
    print()
    
    # Verificar COM5
    print(f"🔍 Verificando {SERIAL_PORT}...")
    if not verificar_com5_disponible():
        print(f"\n❌ ERROR: {SERIAL_PORT} NO está disponible")
        print(f"\n💡 Este script SOLO funciona con {SERIAL_PORT}")
        print(f"❌ NO se conectará a otros puertos (COM11, COM3, etc.)")
        print("\nPuertos disponibles:")
        for p in serial.tools.list_ports.comports():
            print(f"  - {p.device}")
        sys.exit(1)
    
    print(f"✅ {SERIAL_PORT} disponible")
    print(f"📡 Conectando a {SERIAL_PORT}...")
    
    arduino = conectar_com5()
    if not arduino:
        print(f"❌ No se pudo conectar a {SERIAL_PORT}")
        sys.exit(1)
    
    print(f"✅ Conectado exitosamente a {SERIAL_PORT}")
    print(f"📡 Escuchando datos del sensor ultrasónico...")
    print("   Esperando formato: TIMESTAMP:...,NIVEL:...,ESTADO:...")
    print("   (Presiona Ctrl+C para detener)")
    print("-" * 60)
    print()
    
    ultimo_reconexion = 0
    
    try:
        while True:
            # Verificar conexión
            if not arduino.is_open:
                if time.time() - ultimo_reconexion >= DELAY_RECONEXION:
                    ultimo_reconexion = time.time()
                    print(f"⚠️ Reconectando a {SERIAL_PORT}...")
                    if verificar_com5_disponible():
                        arduino = conectar_com5()
                        if arduino:
                            print(f"✅ Reconectado a {SERIAL_PORT}")
                time.sleep(DELAY_LECTURA)
                continue
            
            # Leer datos
            try:
                datos = leer_datos(arduino)
                if datos:
                    procesar_datos(datos)
            except serial.SerialException:
                arduino = None
            except KeyboardInterrupt:
                break
            except:
                pass
            
            time.sleep(DELAY_LECTURA)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Detenido por el usuario")
    finally:
        if arduino and arduino.is_open:
            arduino.close()
        print(f"\n✅ Conexión con {SERIAL_PORT} cerrada")

if __name__ == "__main__":
    main()
