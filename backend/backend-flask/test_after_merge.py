#!/usr/bin/env python3
"""
Script para probar el sistema después de resolver conflictos de merge
"""
import requests
import json

def test_system_after_merge():
    """Probar que todo funcione después del merge"""
    base_url = 'http://localhost:5000'
    
    print("🔄 Probando sistema después de resolver conflictos...")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health check
    try:
        response = requests.get(f'{base_url}/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ 1. Health Check: PASSED")
            tests_passed += 1
        else:
            print(f"❌ 1. Health Check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ 1. Health Check: FAILED (Error: {e})")
    
    # Test 2: Login con admin
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f'{base_url}/api/login', json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'token' in data and 'rol' in data:
                print("✅ 2. Login Admin: PASSED")
                print(f"   Mensaje: {data.get('mensaje')}")
                tests_passed += 1
                admin_token = data['token']
            else:
                print("❌ 2. Login Admin: FAILED (Respuesta incompleta)")
        else:
            print(f"❌ 2. Login Admin: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ 2. Login Admin: FAILED (Error: {e})")
    
    # Test 3: Login con usuario
    try:
        login_data = {"username": "usuario", "password": "usuario123"}
        response = requests.post(f'{base_url}/api/login', json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('rol') == 'usuario':
                print("✅ 3. Login Usuario: PASSED")
                tests_passed += 1
            else:
                print("❌ 3. Login Usuario: FAILED (Rol incorrecto)")
        else:
            print(f"❌ 3. Login Usuario: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ 3. Login Usuario: FAILED (Error: {e})")
    
    # Test 4: Agregar medición
    try:
        test_data = {"distancia": 42.3}
        response = requests.post(f'{base_url}/api/mediciones', json=test_data, timeout=5)
        if response.status_code == 201:
            data = response.json()
            if data.get('mensaje') == 'Medición guardada':
                print("✅ 4. Agregar Medición: PASSED")
                tests_passed += 1
            else:
                print("❌ 4. Agregar Medición: FAILED (Mensaje incorrecto)")
        else:
            print(f"❌ 4. Agregar Medición: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ 4. Agregar Medición: FAILED (Error: {e})")
    
    # Test 5: Obtener mediciones
    try:
        response = requests.get(f'{base_url}/api/mediciones', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ 5. Obtener Mediciones: PASSED ({len(data)} mediciones)")
                if len(data) > 0:
                    print(f"   Última medición: {data[0].get('distancia')} cm")
                tests_passed += 1
            else:
                print("❌ 5. Obtener Mediciones: FAILED (Formato incorrecto)")
        else:
            print(f"❌ 5. Obtener Mediciones: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ 5. Obtener Mediciones: FAILED (Error: {e})")
    
    # Resumen
    print("=" * 60)
    print(f"📊 Resultado: {tests_passed}/{total_tests} tests pasaron")
    
    if tests_passed == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON! Sistema funcionando correctamente")
        print("\n✅ El login funciona igual que antes")
        print("✅ Las mediciones funcionan igual que antes") 
        print("✅ Los conflictos de merge fueron resueltos exitosamente")
        print("\n💡 Tu frontend debería conectar perfectamente ahora")
    else:
        print(f"⚠️  {total_tests - tests_passed} tests fallaron")
        print("🔧 Revisa que el servidor esté corriendo y MongoDB disponible")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = test_system_after_merge()
    exit(0 if success else 1)
