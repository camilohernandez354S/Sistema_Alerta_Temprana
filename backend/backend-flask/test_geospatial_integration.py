#!/usr/bin/env python3
"""
Script de prueba para verificar la integración completa del módulo geoespacial
Prueba todos los endpoints y funcionalidades implementadas
"""
import sys
import os
import requests
import json
import time
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend_health():
    """Probar que el backend esté funcionando"""
    print("🔍 Probando salud del backend...")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando correctamente")
            return True
        else:
            print(f"❌ Backend respondió con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def test_geospatial_health():
    """Probar salud del módulo geoespacial"""
    print("🗺️ Probando salud del módulo geoespacial...")
    
    try:
        response = requests.get("http://localhost:5000/api/geospatial/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Módulo geoespacial funcionando - Sensores: {data.get('sensors_count', 0)}")
            return True
        else:
            print(f"❌ Módulo geoespacial respondió con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al módulo geoespacial: {e}")
        return False

def test_authentication():
    """Probar autenticación y obtener token"""
    print("🔐 Probando autenticación...")
    
    try:
        # Login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:5000/api/login",
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print("✅ Autenticación exitosa")
                return token
            else:
                print("❌ No se recibió token en la respuesta")
                return None
        else:
            print(f"❌ Error en autenticación: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en autenticación: {e}")
        return None

def test_geospatial_endpoints(token):
    """Probar todos los endpoints geoespaciales"""
    print("🌐 Probando endpoints geoespaciales...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Probar obtener sensores
    print("  📍 Probando GET /api/sensores...")
    try:
        response = requests.get("http://localhost:5000/api/sensores", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ {data.get('total', 0)} sensores encontrados")
        else:
            print(f"    ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # 2. Probar consulta de alertas
    print("  🚨 Probando GET /api/alertas...")
    try:
        # Buenos Aires centro
        params = {
            "lat": -34.6037,
            "lng": -58.3816,
            "radio": 5000
        }
        
        response = requests.get(
            "http://localhost:5000/api/alertas",
            headers=headers,
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ {data.get('total', 0)} alertas encontradas en radio de {params['radio']}m")
        else:
            print(f"    ❌ Error: {response.status_code}")
            print(f"    Respuesta: {response.text}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # 3. Probar crear sensor
    print("  ➕ Probando POST /api/sensores...")
    try:
        sensor_data = {
            "sensor_id": "test_sensor_001",
            "lat": -34.6037,
            "lng": -58.3816,
            "nombre": "Sensor de Prueba",
            "descripcion": "Sensor creado durante las pruebas"
        }
        
        response = requests.post(
            "http://localhost:5000/api/sensores",
            headers=headers,
            json=sensor_data,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"    ✅ Sensor {data.get('sensor_id')} {data.get('operation')} exitosamente")
        else:
            print(f"    ❌ Error: {response.status_code}")
            print(f"    Respuesta: {response.text}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # 4. Probar guardar medición
    print("  📊 Probando POST /api/mediciones...")
    try:
        measurement_data = {
            "sensor_id": "test_sensor_001",
            "nivel": 25.5,
            "estado": "normal",
            "lat": -34.6037,
            "lng": -58.3816
        }
        
        response = requests.post(
            "http://localhost:5000/api/mediciones",
            headers=headers,
            json=measurement_data,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"    ✅ Medición guardada: {data.get('nivel')}cm en {data.get('sensor_id')}")
        else:
            print(f"    ❌ Error: {response.status_code}")
            print(f"    Respuesta: {response.text}")
    except Exception as e:
        print(f"    ❌ Error: {e}")

def test_frontend_dependencies():
    """Verificar que las dependencias del frontend estén instaladas"""
    print("📦 Verificando dependencias del frontend...")
    
    try:
        import subprocess
        import os
        
        # Cambiar al directorio del frontend
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        
        # Verificar si node_modules existe
        if os.path.exists(os.path.join(frontend_dir, 'node_modules')):
            print("✅ node_modules encontrado")
            
            # Verificar dependencias específicas
            try:
                result = subprocess.run(
                    ["npm", "list", "leaflet", "vue3-leaflet"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print("✅ Dependencias de Leaflet instaladas")
                else:
                    print("⚠️ Algunas dependencias de Leaflet pueden no estar instaladas")
                    print("   Ejecuta: npm install leaflet vue3-leaflet")
            except Exception as e:
                print(f"⚠️ No se pudo verificar dependencias: {e}")
        else:
            print("❌ node_modules no encontrado")
            print("   Ejecuta: npm install en el directorio frontend")
            
    except Exception as e:
        print(f"⚠️ Error verificando dependencias: {e}")

def test_mongodb_connection():
    """Probar conexión a MongoDB"""
    print("🍃 Probando conexión a MongoDB...")
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Probar conexión
        client.admin.command('ping')
        
        # Verificar colecciones
        db = client['sistema_alerta']
        collections = db.list_collection_names()
        
        print(f"✅ MongoDB conectado - Colecciones: {collections}")
        
        # Verificar índices geoespaciales
        if 'mediciones' in collections:
            indexes = db['mediciones'].list_indexes()
            geo_indexes = [idx for idx in indexes if 'location' in str(idx)]
            if geo_indexes:
                print("✅ Índices geoespaciales encontrados en mediciones")
            else:
                print("⚠️ No se encontraron índices geoespaciales en mediciones")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de integración del módulo geoespacial")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 6
    
    # 1. Probar MongoDB
    if test_mongodb_connection():
        tests_passed += 1
    
    # 2. Probar backend
    if test_backend_health():
        tests_passed += 1
    
    # 3. Probar módulo geoespacial
    if test_geospatial_health():
        tests_passed += 1
    
    # 4. Probar autenticación
    token = test_authentication()
    if token:
        tests_passed += 1
        
        # 5. Probar endpoints geoespaciales
        test_geospatial_endpoints(token)
        tests_passed += 1
    
    # 6. Verificar frontend
    test_frontend_dependencies()
    tests_passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Resultados: {tests_passed}/{total_tests} pruebas completadas")
    
    if tests_passed == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El módulo geoespacial está listo para usar.")
        print("\n🚀 Próximos pasos:")
        print("1. Ejecuta: python setup_geospatial_data.py")
        print("2. Inicia el frontend: npm run dev")
        print("3. Abre: http://localhost:5173")
        print("4. Haz clic en el mapa para buscar alertas")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.")
        print("\n🔧 Soluciones comunes:")
        print("- Asegúrate de que MongoDB esté ejecutándose")
        print("- Verifica que el backend Flask esté iniciado")
        print("- Ejecuta: pip install -r requirements.txt")
        print("- Ejecuta: npm install en el directorio frontend")

if __name__ == "__main__":
    main()
