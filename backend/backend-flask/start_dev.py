#!/usr/bin/env python3
"""
Script para iniciar el entorno de desarrollo
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import flask
        import pymongo
        import pandas
        import sklearn
        print("✅ Dependencias de Python verificadas")
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    return True

def check_mongodb():
    """Verificar conexión a MongoDB"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ Conexión a MongoDB verificada")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("💡 Inicia MongoDB con: docker-compose up -d mongodb")
        return False

def start_backend():
    """Iniciar el backend Flask"""
    print("🚀 Iniciando backend Flask...")
    try:
        # Cambiar al directorio del backend
        backend_dir = Path(__file__).parent
        os.chdir(backend_dir)
        
        # Establecer variables de entorno
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        
        # Importar y ejecutar la aplicación
        from run import main
        main()
        
    except KeyboardInterrupt:
        print("\n👋 Backend detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando backend: {e}")

def main():
    """Función principal"""
    print("🔧 Iniciando entorno de desarrollo...")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar MongoDB (opcional, solo mostrar advertencia)
    check_mongodb()
    
    # Iniciar backend
    start_backend()

if __name__ == '__main__':
    main()
