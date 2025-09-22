# Sistema_Alerta_Temprana/backend/backend-flask/run.py

# CORRECCIÓN FINAL Y DEFINITIVA:
# Se importa 'create_app' desde 'app' (su ubicación real en __init__.py)
from app import create_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear la instancia de la aplicación Flask.
# Esta línea ahora funcionará.
app = create_app({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key'),
    'MONGO_URI': os.getenv('MONGO_URI'),
    'MONGO_DBNAME': os.getenv('MONGO_DB'),
    'DEBUG': os.getenv('FLASK_ENV') == 'development'
})

# Este bloque es correcto y no necesita cambios.
if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"Iniciando servidor de desarrollo de Flask en http://{host}:{port}")
    app.run(host=host, port=port)