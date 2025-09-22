#!/usr/bin/env python3
"""
Script de configuración rápida del sistema
"""
import subprocess
import sys
import os

def install_basic_requirements():
    """Instalar solo las dependencias básicas necesarias"""
    print("📦 Instalando dependencias básicas...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements-basic.txt"
        ])
        print("✅ Dependencias básicas instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def check_mongodb():
    """Verificar si MongoDB está disponible"""
    print("🔍 Verificando MongoDB...")
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB disponible")
        return True
    except Exception as e:
        print("⚠️  MongoDB no disponible - funcionará en modo limitado")
        print(f"   Error: {e}")
        return False

def run_server():
    """Ejecutar el servidor"""
    print("🚀 Iniciando servidor...")
    try:
        subprocess.run([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")

def main():
    """Función principal"""
    print("🛠️  Configuración rápida del Sistema de Alerta Temprana")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('run.py'):
        print("❌ Error: Ejecuta este script desde backend/backend-flask/")
        return
    
    # Instalar dependencias básicas
    if not install_basic_requirements():
        print("❌ No se pudieron instalar las dependencias")
        return
    
    # Verificar MongoDB
    check_mongodb()
    
    # Mostrar instrucciones
    print("\n📋 Sistema configurado!")
    print("💡 Para usar:")
    print("   1. Asegúrate de que MongoDB esté corriendo (opcional)")
    print("   2. Ejecuta: python run.py")
    print("   3. Tu frontend puede conectar a http://localhost:5000")
    print("\n🔐 Credenciales de prueba:")
    print("   Admin: admin / admin123")
    print("   Usuario: usuario / usuario123")
    
    # Preguntar si ejecutar servidor
    response = input("\n¿Ejecutar servidor ahora? (y/n): ").lower().strip()
    if response in ['y', 'yes', 'sí', 's']:
        run_server()

if __name__ == "__main__":
    main()
