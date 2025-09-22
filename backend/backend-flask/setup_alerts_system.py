#!/usr/bin/env python3
"""
Script de configuración rápida para el Sistema de Alertas
Configura MongoDB, crea índices y datos de prueba
"""
import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

def setup_mongodb():
    """Configurar MongoDB para el sistema de alertas"""
    print("🔧 Configurando MongoDB para el sistema de alertas...")
    
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sistema_alerta']
        
        # Crear colecciones si no existen
        collections = ['alertas', 'mediciones']
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"✅ Colección '{collection_name}' creada")
            else:
                print(f"ℹ️  Colección '{collection_name}' ya existe")
        
        # Crear índices para optimización
        alertas_collection = db['alertas']
        mediciones_collection = db['mediciones']
        
        # Índices para alertas
        indices_alertas = [
            [('timestamp', -1)],  # Ordenar por fecha
            [('alerta_activa', 1)],  # Filtrar por estado
            [('tipo_alerta', 1)],  # Filtrar por tipo
            [('desactivada_por', 1)],  # Auditoría
        ]
        
        for indice in indices_alertas:
            try:
                alertas_collection.create_index(indice)
                print(f"✅ Índice creado en alertas: {indice}")
            except Exception as e:
                print(f"⚠️  Índice ya existe o error: {e}")
        
        # Índices para mediciones
        indices_mediciones = [
            [('fecha', -1)],  # Ordenar por fecha
        ]
        
        for indice in indices_mediciones:
            try:
                mediciones_collection.create_index(indice)
                print(f"✅ Índice creado en mediciones: {indice}")
            except Exception as e:
                print(f"⚠️  Índice ya existe o error: {e}")
        
        print("✅ Configuración de MongoDB completada")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando MongoDB: {e}")
        return False

def create_sample_data():
    """Crear datos de prueba para el sistema"""
    print("\n📊 Creando datos de prueba...")
    
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sistema_alerta']
        
        # Limpiar datos existentes (opcional)
        respuesta = input("¿Desea limpiar datos existentes? (y/N): ").lower()
        if respuesta == 'y':
            db['alertas'].delete_many({})
            db['mediciones'].delete_many({})
            print("🗑️  Datos existentes eliminados")
        
        # Crear mediciones de ejemplo
        mediciones_ejemplo = []
        base_time = datetime.utcnow() - timedelta(hours=2)
        
        # Simular datos de las últimas 2 horas
        for i in range(24):  # Una medición cada 5 minutos
            timestamp = base_time + timedelta(minutes=i * 5)
            
            # Simular diferentes niveles
            if i < 8:  # Primera hora: normal
                nivel = 25.0 + (i * 0.5)
            elif i < 16:  # Segunda hora: bajando (hacia inundación)
                nivel = 28.0 - (i - 8) * 2.0
            else:  # Última media hora: inundación
                nivel = 12.0 + (i - 16) * 0.2
            
            mediciones_ejemplo.append({
                'distancia': round(nivel, 1),
                'fecha': timestamp
            })
        
        # Insertar mediciones
        if mediciones_ejemplo:
            db['mediciones'].insert_many(mediciones_ejemplo)
            print(f"✅ {len(mediciones_ejemplo)} mediciones de ejemplo creadas")
        
        # Crear alertas de ejemplo
        alertas_ejemplo = []
        
        # Alerta de sequía (resuelta)
        alertas_ejemplo.append({
            'tipo_alerta': 'sequia',
            'nivel_agua': 42.5,
            'alerta_activa': False,
            'timestamp': datetime.utcnow() - timedelta(hours=3),
            'fecha_desactivacion': datetime.utcnow() - timedelta(hours=2, minutes=30),
            'desactivada_por': 'admin',
            'motivo_desactivacion': 'condiciones_normalizadas',
            'buzzer_activo': False,
            'creada_por': 'arduino_sensor',
            'descripcion': '🏜️ ALERTA DE SEQUÍA: Nivel de agua bajo (42.5 cm). Por encima del umbral de 40.0 cm.'
        })
        
        # Alerta de inundación (activa)
        alertas_ejemplo.append({
            'tipo_alerta': 'inundacion',
            'nivel_agua': 12.5,
            'alerta_activa': True,
            'timestamp': datetime.utcnow() - timedelta(minutes=15),
            'fecha_desactivacion': None,
            'desactivada_por': None,
            'motivo_desactivacion': None,
            'buzzer_activo': True,
            'creada_por': 'arduino_sensor',
            'descripcion': '🌊 ALERTA DE INUNDACIÓN: Nivel de agua crítico (12.5 cm). Por debajo del umbral de 15.0 cm.'
        })
        
        # Insertar alertas
        if alertas_ejemplo:
            db['alertas'].insert_many(alertas_ejemplo)
            print(f"✅ {len(alertas_ejemplo)} alertas de ejemplo creadas")
        
        print("✅ Datos de prueba creados exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False

def verify_system():
    """Verificar que el sistema esté funcionando correctamente"""
    print("\n🔍 Verificando sistema de alertas...")
    
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sistema_alerta']
        
        # Verificar colecciones
        mediciones_count = db['mediciones'].count_documents({})
        alertas_count = db['alertas'].count_documents({})
        alertas_activas = db['alertas'].count_documents({'alerta_activa': True})
        
        print(f"📊 Mediciones en base de datos: {mediciones_count}")
        print(f"🚨 Total de alertas: {alertas_count}")
        print(f"🔴 Alertas activas: {alertas_activas}")
        
        # Verificar última medición
        ultima_medicion = db['mediciones'].find_one(sort=[('fecha', -1)])
        if ultima_medicion:
            print(f"📏 Última medición: {ultima_medicion['distancia']} cm ({ultima_medicion['fecha']})")
        
        # Verificar alertas activas
        alertas_activas_list = list(db['alertas'].find({'alerta_activa': True}))
        for alerta in alertas_activas_list:
            print(f"⚠️  Alerta activa: {alerta['tipo_alerta']} - {alerta['nivel_agua']} cm")
        
        print("✅ Verificación del sistema completada")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando sistema: {e}")
        return False

def create_env_template():
    """Crear template de archivo .env"""
    print("\n📝 Creando template de configuración...")
    
    env_content = """# Configuración del Sistema de Alertas
# =====================================

# Umbrales de alerta (en centímetros)
UMBRAL_INUNDACION=15.0
UMBRAL_SEQUIA=40.0

# Comunicación con Arduino
SERIAL_PORT=COM11
BAUD_RATE=9600
IOT_DEVICE_URL=

# Base de datos MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=sistema_alerta

# Servidor Flask
FLASK_SERVER_URL=http://localhost:5000
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=supersecreto

# Logging
LOG_LEVEL=INFO
"""
    
    env_file = '.env.example'
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Template de configuración creado: {env_file}")
        print("📌 Copia este archivo a .env y ajusta los valores según tu configuración")
        return True
    except Exception as e:
        print(f"❌ Error creando template: {e}")
        return False

def main():
    """Función principal del script de configuración"""
    print("🚨 Sistema de Alerta Temprana - Configuración de Alertas")
    print("=" * 60)
    
    # Verificar dependencias
    try:
        import pymongo
        print("✅ pymongo disponible")
    except ImportError:
        print("❌ pymongo no encontrado. Instala con: pip install pymongo")
        sys.exit(1)
    
    # Menú de opciones
    while True:
        print("\n📋 Opciones disponibles:")
        print("1. Configurar MongoDB (crear colecciones e índices)")
        print("2. Crear datos de prueba")
        print("3. Verificar sistema")
        print("4. Crear template de configuración (.env.example)")
        print("5. Configuración completa (1+2+4)")
        print("0. Salir")
        
        opcion = input("\n🔸 Selecciona una opción (0-5): ").strip()
        
        if opcion == '1':
            setup_mongodb()
        elif opcion == '2':
            create_sample_data()
        elif opcion == '3':
            verify_system()
        elif opcion == '4':
            create_env_template()
        elif opcion == '5':
            print("\n🚀 Iniciando configuración completa...")
            if setup_mongodb():
                if create_sample_data():
                    create_env_template()
                    print("\n🎉 Configuración completa terminada!")
                    print("\n📋 Próximos pasos:")
                    print("1. Copia .env.example a .env y ajusta la configuración")
                    print("2. Inicia el servidor Flask: python run.py")
                    print("3. Inicia el frontend: npm run dev")
                    print("4. Conecta el Arduino y ejecuta: python leer_serial.py")
        elif opcion == '0':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida")

if __name__ == '__main__':
    main()
