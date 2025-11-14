"""
Script para verificar puertos seriales disponibles
Útil para configurar el puerto correcto en .env
"""
import serial.tools.list_ports

print("=" * 60)
print("Puertos Seriales Disponibles")
print("=" * 60)
print()

puertos = list(serial.tools.list_ports.comports())

if not puertos:
    print("❌ No se encontraron puertos seriales disponibles")
    print()
    print("Verifica que:")
    print("  1. Tu Arduino/ESP8266 esté conectado por USB")
    print("  2. Los drivers estén instalados correctamente")
    print("  3. El dispositivo esté encendido")
else:
    print(f"✅ Se encontraron {len(puertos)} puerto(s) serial(es):\n")
    for i, puerto in enumerate(puertos, 1):
        print(f"  [{i}] {puerto.device}")
        print(f"      Descripción: {puerto.description}")
        if puerto.manufacturer:
            print(f"      Fabricante: {puerto.manufacturer}")
        if puerto.serial_number:
            print(f"      Número de serie: {puerto.serial_number}")
        print()

print("=" * 60)
print("Para usar este puerto, crea/edita el archivo:")
print("  backend/backend-flask/.env")
print()
print("Y agrega:")
print("  SERIAL_PORT=COMX")
print("  BAUD_RATE=115200")
print("  FLASK_SERVER_URL=http://localhost:5000")
print()
print("Donde COMX es el puerto que quieres usar (ej: COM3, COM7)")
print("=" * 60)

