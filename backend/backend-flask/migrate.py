"""
Script de migración para inicializar la base de datos MongoDB
Crea colecciones, índices y datos iniciales si es necesario
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Intentar cargar desde la raíz del proyecto
    root_env = Path(__file__).resolve().parent.parent.parent / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env)

def get_mongo_config():
    """Obtener configuración de MongoDB desde variables de entorno"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB', 'sistema_alerta')
    
    # Si estamos en Docker, corregir el nombre del servicio
    # El servicio en docker-compose se llama 'mongo', no 'sat-mongo'
    if 'sat-mongo' in mongo_uri:
        # Reemplazar sat-mongo por mongo (nombre del servicio en docker-compose)
        mongo_uri = mongo_uri.replace('sat-mongo', 'mongo')
        print(f"⚠️  Corregido MONGO_URI: usando 'mongo' en lugar de 'sat-mongo'")
    elif 'localhost' in mongo_uri and os.path.exists('/.dockerenv'):
        # Si estamos en Docker y la URI apunta a localhost, usar el nombre del servicio
        mongo_uri = 'mongodb://mongo:27017/'
        print(f"⚠️  Detectado Docker: usando 'mongo' como nombre del servicio")
    
    return mongo_uri, db_name

def migrate_database():
    """Ejecutar migración de la base de datos"""
    print("🚀 Iniciando migración de base de datos...")
    
    try:
        # Obtener configuración
        mongo_uri, db_name = get_mongo_config()
        print(f"📡 Conectando a MongoDB: {mongo_uri}")
        print(f"📦 Base de datos: {db_name}")
        
        # Crear conexión
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Verificar conexión
        client.admin.command('ping')
        print("✅ Conexión a MongoDB establecida")
        
        # 1. Crear colecciones
        print("\n📋 Creando colecciones...")
        collections = ['mediciones', 'sensores', 'alertas', 'usuarios']
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"  ✅ Colección '{collection_name}' creada")
            else:
                count = db[collection_name].count_documents({})
                print(f"  ℹ️  Colección '{collection_name}' ya existe ({count} documentos)")
        
        # 2. Crear índices geoespaciales
        print("\n🗺️  Creando índices geoespaciales...")
        try:
            # Índice en mediciones
            db['mediciones'].create_index([("location", "2dsphere")], name="location_2dsphere")
            print("  ✅ Índice geoespacial creado en 'mediciones'")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("  ℹ️  Índice geoespacial en 'mediciones' ya existe")
            else:
                print(f"  ⚠️  Error creando índice en 'mediciones': {e}")
        
        try:
            # Índice en sensores
            db['sensores'].create_index([("location", "2dsphere")], name="location_2dsphere")
            print("  ✅ Índice geoespacial creado en 'sensores'")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("  ℹ️  Índice geoespacial en 'sensores' ya existe")
            else:
                print(f"  ⚠️  Error creando índice en 'sensores': {e}")
        
        # 3. Crear índices adicionales para mejor rendimiento
        print("\n⚡ Creando índices adicionales...")
        
        # Índice en timestamp para mediciones
        try:
            db['mediciones'].create_index([("timestamp", -1)], name="timestamp_desc")
            print("  ✅ Índice de timestamp creado en 'mediciones'")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("  ℹ️  Índice de timestamp en 'mediciones' ya existe")
        
        # Índice en sensor_id para mediciones
        try:
            db['mediciones'].create_index([("sensor_id", 1)], name="sensor_id_idx")
            print("  ✅ Índice de sensor_id creado en 'mediciones'")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("  ℹ️  Índice de sensor_id en 'mediciones' ya existe")
        
        # Índice en estado para alertas
        try:
            db['alertas'].create_index([("estado", 1), ("timestamp", -1)], name="estado_timestamp_idx")
            print("  ✅ Índice compuesto creado en 'alertas'")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("  ℹ️  Índice compuesto en 'alertas' ya existe")
        
        # 4. Crear usuarios iniciales si no existen
        print("\n👤 Verificando usuarios iniciales...")
        usuarios_collection = db['usuarios']
        usuarios_count = usuarios_collection.count_documents({})
        
        if usuarios_count == 0:
            print("  ℹ️  No hay usuarios en la base de datos")
            print("  💡 Ejecuta 'python create_user.py --default' para crear usuarios por defecto")
            print("  💡 O ejecuta 'python create_user.py' para crear un usuario personalizado")
        else:
            print(f"  ✅ {usuarios_count} usuario(s) encontrado(s) en la base de datos")
            usuarios = usuarios_collection.find({}, {'username': 1, 'rol': 1, '_id': 0})
            for usuario in usuarios:
                print(f"     - {usuario.get('username')} ({usuario.get('rol')})")
        
        # 5. Verificar estado final
        print("\n📊 Estado final de la base de datos:")
        db_stats = db.command("dbStats")
        print(f"  📦 Tamaño: {db_stats.get('dataSize', 0) / 1024:.2f} KB")
        print(f"  📋 Colecciones: {len(db.list_collection_names())}")
        print(f"  🔍 Índices: {db_stats.get('indexes', 0)}")
        
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            indexes = db[collection_name].index_information()
            print(f"  - {collection_name}: {count} documentos, {len(indexes)} índices")
        
        # Cerrar conexión
        client.close()
        
        print("\n✅ Migración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)

