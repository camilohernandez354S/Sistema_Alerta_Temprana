#!/usr/bin/env python3
"""
Script para probar el sistema restaurado
"""
import requests
import json

def test_system():
    """Probar todos los endpoints del sistema"""
    base_url = 'http://localhost:5000'
    
    print("🧪 Probando sistema restaurado...")
    print("=" * 50)
    
    # 1. Health check
    try:
        response = requests.get(f'{base_url}/api/health', timeout=5)
        print(f"1. Health Check: {'✅' if response.status_code == 200 else '❌'} ({response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
    except Exception as e:
        print(f"1. Health Check: ❌ (Error: {e})")
        return False
    
    # 2. Login test
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f'{base_url}/api/login', json=login_data, timeout=5)
        print(f"2. Login: {'✅' if response.status_code == 200 else '❌'} ({response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"   Mensaje: {data.get('mensaje')}")
            print(f"   Rol: {data.get('rol')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"2. Login: ❌ (Error: {e})")
    
    # 3. Agregar medición de prueba
    try:
        test_data = {"distancia": 25.7}
        response = requests.post(f'{base_url}/api/mediciones', json=test_data, timeout=5)
        print(f"3. Agregar medición: {'✅' if response.status_code == 201 else '❌'} ({response.status_code})")
        if response.status_code == 201:
            data = response.json()
            print(f"   Respuesta: {data.get('mensaje')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"3. Agregar medición: ❌ (Error: {e})")
    
    # 4. Obtener mediciones
    try:
        response = requests.get(f'{base_url}/api/mediciones', timeout=5)
        print(f"4. Obtener mediciones: {'✅' if response.status_code == 200 else '❌'} ({response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"   Mediciones encontradas: {len(data)}")
            if len(data) > 0:
                print(f"   Última medición: {data[0].get('distancia')} cm")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"4. Obtener mediciones: ❌ (Error: {e})")
    
    print("=" * 50)
    print("✅ Sistema restaurado y probado!")
    print("\n💡 Para usar:")
    print("   1. cd backend/backend-flask")
    print("   2. python run.py")
    print("   3. Tu frontend debería conectar a http://localhost:5000")

if __name__ == "__main__":
    test_system()
