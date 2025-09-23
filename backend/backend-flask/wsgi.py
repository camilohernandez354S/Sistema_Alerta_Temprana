"""
Archivo WSGI para Gunicorn
Punto de entrada para el servidor de producción
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar la aplicación Flask
from app import create_app

# Crear la instancia de la aplicación
application = create_app({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key'),
    'MONGO_URI': os.getenv('MONGO_URI'),
    'MONGO_DB': os.getenv('MONGO_DB'),
    'DEBUG': os.getenv('FLASK_ENV') == 'development'
})

# Gunicorn necesita la variable 'application'
# Esta es la aplicación WSGI que Gunicorn ejecutará
if __name__ == "__main__":
    # Solo para desarrollo local
    application.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
