"""
Sistema de Alerta Temprana - Servidor de Desarrollo
Archivo para ejecutar la aplicación en modo desarrollo local
"""

from app import create_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear la instancia de la aplicación Flask
app = create_app({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key'),
    'MONGO_URI': os.getenv('MONGO_URI'),
    'MONGO_DB': os.getenv('MONGO_DB'),
    'DEBUG': os.getenv('FLASK_ENV') == 'development'
})

# Ejecutar solo en modo desarrollo
if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando Sistema de Alerta Temprana en modo desarrollo")
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"🔧 Debug: {debug}")
    print(f"🗄️ Base de datos: {os.getenv('MONGO_DB', 'sistema_alerta')}")
    
    app.run(host=host, port=port, debug=debug)