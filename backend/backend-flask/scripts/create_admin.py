#!/usr/bin/env python3
"""
Script para crear usuario administrador inicial
"""
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from pymongo import MongoClient
from app.models.user_model import UserCreate, UserRole
from app.repositories.user_repository import UserRepository

def create_admin_user():
    """Crear usuario administrador inicial"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración de MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB', 'sensor_database')
    
    try:
        # Conectar a MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Verificar conexión
        client.server_info()
        print("✅ Conexión a MongoDB establecida")
        
        # Crear repository
        user_repository = UserRepository(client, db_name)
        
        # Verificar si el usuario admin ya existe
        existing_user = user_repository.find_by_username("admin")
        if existing_user:
            print("✅ Usuario administrador ya existe")
            print(f"   Username: {existing_user['username']}")
            print(f"   Email: {existing_user['email']}")
            print(f"   Rol: {existing_user['role']}")
            print("\n🔑 Credenciales de acceso:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            return
        
        # Datos del administrador
        import bcrypt
        from datetime import datetime
        
        # Hashear contraseña
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), salt)
        
        # Crear usuario directamente en la base de datos
        user_dict = {
            'username': 'admin',
            'email': 'admin@sistema.com',
            'full_name': 'Administrador del Sistema',
            'role': 'admin',
            'password': hashed_password.decode('utf-8'),
            'location': 'Central',
            'status': 'active',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Insertar usuario
        user_id = user_repository.insert_one(user_dict)
        
        if user_id:
            print("✅ Usuario administrador creado exitosamente")
            print(f"   Username: admin")
            print(f"   Email: admin@sistema.com")
            print(f"   Rol: admin")
            print(f"   Ubicación: Central")
            print("\n🔑 Credenciales de acceso:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        else:
            print("❌ Error creando usuario administrador")
            print("   Verifica que MongoDB esté corriendo y que no exista ya un usuario 'admin'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Verifica que MongoDB esté corriendo en localhost:27017")

if __name__ == '__main__':
    print("🔧 Creando usuario administrador inicial...")
    create_admin_user()
