#!/usr/bin/env python3
"""
Script rápido para probar el sistema
"""
import requests
import json

def test_endpoints():
    """Probar los endpoints principales"""
    base_url = 'http://localhost:5000'
    
    print("🧪 Probando endpoints del sistema...")
    print("-" * 40)
    
    # 1. Probar health check
    try:
        response = requests.get(f'{base_url}/api/health')
        print(f"1. Health Check: {'✅' if response.status_code == 200 else '❌'} ({response.status_code})")
    except:
        print("1. Health Check: ❌ (No conecta)")
        return
    
    # 2. Probar login
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f'{base_url}/api/login', json=login_data)
        print(f"2. Login: {'✅' if response.status_code == 200 else '❌'} ({response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"   Mensaje: {data.get('mensaje')}")
    except:
        print("2. Login: ❌ (Error)")
    
    # 3. Probar obtener mediciones
    try:
        response = requests.get(f'{base_url}/api/mediciones')
        print(f"3. Get Mediciones: {'✅' if response.status_code == 200 else '❌'} ({response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"   Mediciones encontradas: {len(data)}")
        else:
            print(f"   Error: {response.text}")
    except:
        print("3. Get Mediciones: ❌ (Error)")
    
    # 4. Agregar una medición de prueba
    try:
        test_data = {"distancia": 25.5}
        response = requests.post(f'{base_url}/api/mediciones', json=test_data)
        print(f"4. Post Medición: {'✅' if response.status_code == 201 else '❌'} ({response.status_code})")
        if response.status_code == 201:
            data = response.json()
            print(f"   Respuesta: {data.get('mensaje')}")
    except:
        print("4. Post Medición: ❌ (Error)")
    
    # 5. Verificar mediciones después de agregar
    try:
        response = requests.get(f'{base_url}/api/mediciones')
        if response.status_code == 200:
            data = response.json()
            print(f"5. Verificación final: ✅ ({len(data)} mediciones)")
            if len(data) > 0:
                print(f"   Última medición: {data[0].get('distancia')} cm")
        else:
            print("5. Verificación final: ❌")
    except:
        print("5. Verificación final: ❌ (Error)")

if __name__ == "__main__":
    test_endpoints()
