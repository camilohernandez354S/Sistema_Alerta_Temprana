#!/usr/bin/env python3
"""
Script de configuración para la integración de Arduino
Configura el entorno y verifica que todo esté funcionando
"""
import os
import sys
from pathlib import Path

def setup_arduino_integration():
    """Configurar la integración de Arduino"""
    print("🔧 Configurando integración de Arduino")
    print("=" * 50)
    
    # Verificar archivo .env
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("❌ Archivo .env no encontrado")
        print("💡 Creando archivo .env con configuración básica...")
        
        env_content = """# Configuración del servidor Flask
FLASK_SERVER_URL=http://localhost:5000

# Configuración del puerto serial Arduino
SERIAL_PORT=COM11
BAUD_RATE=9600

# Configuración de MongoDB
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=sistema_alerta_temprana

# Configuración de alertas
ALERT_EMAIL_SMTP_SERVER=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=tu_email@gmail.com
ALERT_EMAIL_PASSWORD=tu_password
ALERT_EMAIL_FROM=tu_email@gmail.com
"""
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado")
        print("⚠️  Recuerda configurar tus credenciales de email en el .env")
    else:
        print("✅ Archivo .env encontrado")
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    try:
        import requests
        print("✅ requests instalado")
    except ImportError:
        print("❌ requests no instalado")
        print("💡 Ejecuta: pip install requests")
    
    try:
        import serial
        print("✅ pyserial instalado")
    except ImportError:
        print("❌ pyserial no instalado")
        print("💡 Ejecuta: pip install pyserial")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv instalado")
    except ImportError:
        print("❌ python-dotenv no instalado")
        print("💡 Ejecuta: pip install python-dotenv")
    
    # Mostrar opciones de uso
    print("\n🚀 Opciones de uso:")
    print("=" * 30)
    print("1. Usar el lector serial integrado:")
    print("   python arduino_serial_reader.py")
    print()
    print("2. Usar el lector serial original (actualizado):")
    print("   cd ../arduino && python leer_serial.py")
    print()
    print("3. Probar el servicio:")
    print("   python test_arduino_service.py")
    print()
    print("4. Iniciar el servidor Flask:")
    print("   python run.py")
    
    print("\n📋 Configuración recomendada:")
    print("- Configura SERIAL_PORT en .env con tu puerto Arduino")
    print("- Asegúrate de que el servidor Flask esté ejecutándose")
    print("- El Arduino debe estar conectado y enviando datos")
    
    print("\n✅ Configuración completada")

if __name__ == "__main__":
    setup_arduino_integration()
