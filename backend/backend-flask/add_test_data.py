#!/usr/bin/env python3
"""
Script para agregar datos de prueba al sistema
"""
import requests
import json
from datetime import datetime, timedelta
import random

def add_test_measurements():
    """Agregar mediciones de prueba"""
    base_url = 'http://localhost:5000'
    
    print("🔄 Agregando mediciones de prueba...")
    
    # Generar 20 mediciones de prueba de los últimos días
    measurements = []
    for i in range(20):
        # Generar distancia aleatoria entre 5 y 50 cm
        distancia = round(random.uniform(5.0, 50.0), 1)
        measurements.append(distancia)
    
    # Enviar mediciones
    success_count = 0
    for i, distancia in enumerate(measurements):
        try:
            response = requests.post(
                f'{base_url}/api/mediciones',
                json={'distancia': distancia},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 201:
                success_count += 1
                print(f"✅ Medición {i+1}: {distancia} cm")
            else:
                print(f"❌ Error en medición {i+1}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error enviando medición {i+1}: {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(measurements)} mediciones agregadas")
    return success_count > 0

def test_get_measurements():
    """Probar obtener mediciones"""
    try:
        print("\n🔍 Probando obtener mediciones...")
        response = requests.get('http://localhost:5000/api/mediciones', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Obtenidas {len(data)} mediciones")
            
            if len(data) > 0:
                print("📋 Últimas 3 mediciones:")
                for i, medicion in enumerate(data[:3]):
                    print(f"   {i+1}. Distancia: {medicion.get('distancia')} cm - Fecha: {medicion.get('fecha')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo mediciones: {e}")
        return False

def test_backend_connection():
    """Probar conexión con el backend"""
    try:
        print("🔍 Probando conexión con backend...")
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend conectado correctamente")
            return True
        else:
            print(f"❌ Backend responde con error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend")
        print("   ¿Está corriendo 'python run.py' en backend/backend-flask?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Script para agregar datos de prueba")
    print("=" * 50)
    
    # Probar conexión
    if not test_backend_connection():
        return
    
    # Agregar datos de prueba
    if add_test_measurements():
        print("\n🎉 Datos de prueba agregados exitosamente!")
    else:
        print("\n❌ Error agregando datos de prueba")
        return
    
    # Probar obtener datos
    if test_get_measurements():
        print("\n✅ ¡Todo funciona correctamente!")
        print("\n💡 Ahora tu dashboard debería mostrar datos en lugar de 'Error de conexión'")
    else:
        print("\n❌ Error obteniendo datos")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
