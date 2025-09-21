#!/usr/bin/env python3
"""
Script simple para crear usuario administrador inicial
"""
import os
import sys
from pathlib import Path
import bcrypt
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

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
        collection = db['users']
        
        # Verificar conexión
        client.server_info()
        print("✅ Conexión a MongoDB establecida")
        
        # Verificar si el usuario admin ya existe
        existing_user = collection.find_one({"username": "admin"})
        if existing_user:
            print("✅ Usuario administrador ya existe")
            print(f"   Username: {existing_user['username']}")
            print(f"   Email: {existing_user['email']}")
            print(f"   Rol: {existing_user['role']}")
            print("\n🔑 Credenciales de acceso:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            return
        
        # Crear índices si no existen
        try:
            collection.create_index("username", unique=True)
            collection.create_index("email", unique=True)
            collection.create_index("role")
            collection.create_index("status")
            collection.create_index("location")
            print("✅ Índices de usuarios verificados/creados")
        except Exception as e:
            print(f"⚠️  Advertencia creando índices: {e}")
        
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
        result = collection.insert_one(user_dict)
        
        if result.inserted_id:
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
