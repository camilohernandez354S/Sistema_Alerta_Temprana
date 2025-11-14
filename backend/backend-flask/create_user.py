"""
Script para crear usuarios en la base de datos MongoDB
Inserta usuarios con contraseñas hasheadas usando bcrypt
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import bcrypt

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
    if 'sat-mongo' in mongo_uri:
        mongo_uri = mongo_uri.replace('sat-mongo', 'mongo')
    elif 'localhost' in mongo_uri and os.path.exists('/.dockerenv'):
        mongo_uri = 'mongodb://mongo:27017/'
    
    return mongo_uri, db_name

def hash_password(password: str) -> str:
    """Hashear contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_user(username: str, password: str, rol: str = 'usuario', email: str = None):
    """Crear un usuario en la base de datos"""
    print(f"🚀 Creando usuario: {username}")
    
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
        
        # Verificar si la colección usuarios existe
        if 'usuarios' not in db.list_collection_names():
            db.create_collection('usuarios')
            print("✅ Colección 'usuarios' creada")
        
        # Verificar si el usuario ya existe
        usuarios_collection = db['usuarios']
        existing_user = usuarios_collection.find_one({'username': username})
        
        if existing_user:
            print(f"⚠️  El usuario '{username}' ya existe")
            respuesta = input("¿Deseas actualizar la contraseña? (s/n): ").lower()
            if respuesta != 's':
                print("❌ Operación cancelada")
                client.close()
                return False
            
            # Actualizar usuario existente
            hashed_password = hash_password(password)
            usuarios_collection.update_one(
                {'username': username},
                {
                    '$set': {
                        'password': hashed_password,
                        'rol': rol,
                        'email': email,
                        'actualizado_en': datetime.utcnow()
                    }
                }
            )
            print(f"✅ Usuario '{username}' actualizado exitosamente")
        else:
            # Crear nuevo usuario
            hashed_password = hash_password(password)
            nuevo_usuario = {
                'username': username,
                'password': hashed_password,
                'rol': rol,
                'email': email,
                'activo': True,
                'creado_en': datetime.utcnow(),
                'actualizado_en': datetime.utcnow()
            }
            
            result = usuarios_collection.insert_one(nuevo_usuario)
            print(f"✅ Usuario '{username}' creado exitosamente")
            print(f"   ID: {result.inserted_id}")
            print(f"   Rol: {rol}")
        
        # Cerrar conexión
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error creando usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_default_users():
    """Crear usuarios por defecto del sistema"""
    print("🚀 Creando usuarios por defecto...\n")
    
    usuarios_default = [
        {
            'username': 'admin',
            'password': 'admin123',
            'rol': 'admin',
            'email': 'admin@sistema-alerta.local'
        },
        {
            'username': 'usuario',
            'password': 'usuario123',
            'rol': 'usuario',
            'email': 'usuario@sistema-alerta.local'
        }
    ]
    
    for usuario in usuarios_default:
        create_user(
            username=usuario['username'],
            password=usuario['password'],
            rol=usuario['rol'],
            email=usuario['email']
        )
        print()  # Línea en blanco entre usuarios

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo interactivo: crear usuario personalizado
        if sys.argv[1] == '--default' or sys.argv[1] == '-d':
            create_default_users()
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Uso:")
            print("  python create_user.py                    # Modo interactivo")
            print("  python create_user.py --default         # Crear usuarios por defecto")
            print("  python create_user.py username password [rol] [email]")
        elif len(sys.argv) >= 3:
            username = sys.argv[1]
            password = sys.argv[2]
            rol = sys.argv[3] if len(sys.argv) > 3 else 'usuario'
            email = sys.argv[4] if len(sys.argv) > 4 else None
            create_user(username, password, rol, email)
        else:
            print("❌ Uso incorrecto. Usa --help para ver las opciones")
    else:
        # Modo interactivo
        print("=== Crear Usuario en Sistema de Alerta Temprana ===\n")
        username = input("Usuario: ").strip()
        password = input("Contraseña: ").strip()
        rol = input("Rol (admin/usuario) [usuario]: ").strip() or 'usuario'
        email = input("Email (opcional): ").strip() or None
        
        if not username or not password:
            print("❌ Usuario y contraseña son obligatorios")
            sys.exit(1)
        
        if rol not in ['admin', 'usuario']:
            print("⚠️  Rol inválido, usando 'usuario' por defecto")
            rol = 'usuario'
        
        create_user(username, password, rol, email)

