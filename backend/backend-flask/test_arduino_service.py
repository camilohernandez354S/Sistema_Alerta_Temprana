#!/usr/bin/env python3
"""
Script de prueba para el ArduinoClientService integrado
"""
import sys
from pathlib import Path

# Agregar el directorio app al path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.arduino_client_service import arduino_client_service

def test_arduino_service():
    """Probar el servicio de Arduino"""
    print("🧪 Probando ArduinoClientService integrado")
    print("=" * 50)
    
    # Test 1: Formato legacy
    print("\n1️⃣ Probando formato legacy...")
    response1 = arduino_client_service.send_raw_reading("nivel_agua: 25.5 cm")
    print(f"📥 Respuesta: {response1}")
    
    # Test 2: Formato nuevo
    print("\n2️⃣ Probando formato nuevo...")
    response2 = arduino_client_service.send_raw_reading("TIMESTAMP:5016,NIVEL:240.65,ESTADO:Sequía")
    print(f"📥 Respuesta: {response2}")
    
    # Test 3: Formato JSON ESP8266
    print("\n3️⃣ Probando formato JSON ESP8266...")
    response3 = arduino_client_service.send_raw_reading('{"TIMESTAMP":5016,"NIVEL":25.5,"ESTADO":"Normal"}')
    print(f"📥 Respuesta: {response3}")
    
    # Test 4: Método directo
    print("\n4️⃣ Probando método directo...")
    response4 = arduino_client_service.send_measurement_direct(
        distancia=30.2,
        estado="Normal",
        timestamp=6000
    )
    print(f"📥 Respuesta: {response4}")
    
    # Test 5: Mensaje de inicialización
    print("\n5️⃣ Probando mensaje de inicialización...")
    response5 = arduino_client_service.send_raw_reading("=== Sistema inicializado ===")
    print(f"📥 Respuesta: {response5}")
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    test_arduino_service()
