#!/usr/bin/env python3
"""
Script para iniciar el lector de Arduino
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def create_env_file_auto():
    """Crear archivo .env automáticamente"""
    try:
        import serial.tools.list_ports
        
        env_path = Path(__file__).parent / "../backend-flask/.env"
        
        # Obtener puertos disponibles
        ports = list(serial.tools.list_ports.comports())
        available_ports = [p.device for p in ports]
        
        if not available_ports:
            print("❌ No se encontraron puertos seriales disponibles")
            return False
        
        # Usar el primer puerto disponible
        default_port = available_ports[0]
        
        # Contenido del archivo .env
        env_content = f"""# Configuración de la aplicación
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=dev-secret-key-change-in-production

# Configuración de MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=sensor_database
MONGO_COLLECTION=sensor_readings

# Para testing
MONGO_DB_TEST=sensor_database_test

# Configuración de CORS
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=app.log

# Configuración de Arduino (para leer_serial.py)
SERIAL_PORT={default_port}
BAUD_RATE=9600

# Configuración de seguridad (opcional)
REQUIRE_API_KEY=false
API_KEY=your-api-key-here
"""
        
        # Crear directorio si no existe
        env_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escribir archivo
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Archivo .env creado en {env_path}")
        print(f"📡 Puerto configurado: {default_port}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False

def check_dependencies():
    """Verificar dependencias de Arduino"""
    try:
        import serial
        import requests
        print("✅ Dependencias de Arduino verificadas")
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("Ejecuta: pip install pyserial requests python-dotenv")
        return False

def check_arduino_connection():
    """Verificar conexión al Arduino"""
    try:
        import serial.tools.list_ports
        
        # Cargar configuración
        env_path = Path(__file__).parent / "../backend-flask/.env"
        
        # Si no existe el archivo .env, intentar crearlo
        if not env_path.exists():
            print("📝 Archivo .env no encontrado, intentando crear configuración automática...")
            if not create_env_file_auto():
                print("❌ No se pudo crear el archivo .env automáticamente")
                return False
        
        load_dotenv(dotenv_path=env_path)
        
        port = os.getenv("SERIAL_PORT", "COM7")
        
        # Listar puertos disponibles
        ports = list(serial.tools.list_ports.comports())
        available_ports = [p.device for p in ports]
        
        if not available_ports:
            print("❌ No se encontraron puertos seriales disponibles")
            return False
            
        print(f"📡 Puertos disponibles: {', '.join(available_ports)}")
        
        if port not in available_ports:
            print(f"❌ Puerto {port} no encontrado")
            print(f"💡 Actualiza SERIAL_PORT en .env con uno de: {', '.join(available_ports)}")
            return False
            
        print(f"✅ Puerto {port} encontrado")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando puertos: {e}")
        return False

def check_backend_connection():
    """Verificar conexión al backend"""
    try:
        import requests
        
        # Cargar configuración
        env_path = Path(__file__).parent / "../backend-flask/.env"
        load_dotenv(dotenv_path=env_path)
        
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        
        response = requests.get(f"{backend_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Conexión al backend verificada")
            return True
        else:
            print(f"❌ Backend respondió con código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al backend")
        print("💡 Asegúrate de que el backend esté corriendo en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error verificando backend: {e}")
        return False

def start_arduino_reader():
    """Iniciar el lector de Arduino"""
    print("🚀 Iniciando lector de Arduino...")
    try:
        # Cambiar al directorio del Arduino
        arduino_dir = Path(__file__).parent
        os.chdir(arduino_dir)
        
        # Importar y ejecutar el lector
        from leer_serial import main
        main()
        
    except KeyboardInterrupt:
        print("\n👋 Lector de Arduino detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando lector: {e}")

def main():
    """Función principal"""
    print("🔧 Iniciando lector de Arduino...")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar conexión Arduino
    if not check_arduino_connection():
        print("⚠️  Continuando sin verificación de Arduino...")
    
    # Verificar conexión backend
    if not check_backend_connection():
        print("⚠️  Continuando sin verificación de backend...")
    
    # Iniciar lector
    start_arduino_reader()

if __name__ == '__main__':
    main()
