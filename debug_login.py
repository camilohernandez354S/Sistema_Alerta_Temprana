#!/usr/bin/env python3
"""
Script para depurar el problema del login de admin
"""
import requests
import json

def test_login_debug():
    """Probar login con debug detallado"""
    base_url = 'http://localhost:5000'
    
    print("🔍 Depurando problema de login de admin...")
    print("=" * 60)
    
    # Test 1: Verificar que el servidor responda
    print("1. 🌐 Verificando servidor...")
    try:
        response = requests.get(f'{base_url}/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Servidor OK: {data}")
        else:
            print(f"   ❌ Servidor error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ No se puede conectar: {e}")
        return
    
    # Test 2: Probar login con admin (exactamente como el frontend)
    print("\n2. 🔐 Probando login admin...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print(f"   📤 Enviando: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(
            f'{base_url}/api/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📋 Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"   📄 Respuesta: {json.dumps(data, indent=2)}")
        except:
            print(f"   📄 Respuesta (texto): {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Login admin EXITOSO")
        else:
            print("   ❌ Login admin FALLÓ")
            
    except Exception as e:
        print(f"   ❌ Error en petición: {e}")
    
    # Test 3: Probar login con usuario
    print("\n3. 👤 Probando login usuario...")
    try:
        login_data = {
            "username": "usuario",
            "password": "usuario123"
        }
        
        response = requests.post(
            f'{base_url}/api/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login usuario EXITOSO: {data.get('mensaje')}")
        else:
            print(f"   ❌ Login usuario FALLÓ: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Probar credenciales incorrectas
    print("\n4. 🚫 Probando credenciales incorrectas...")
    try:
        login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        
        response = requests.post(
            f'{base_url}/api/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"   ✅ Error manejado correctamente: {data.get('error')}")
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Probar diferentes variaciones de admin
    print("\n5. 🔧 Probando variaciones...")
    
    test_cases = [
        {"username": "admin", "password": "admin123"},
        {"username": "Admin", "password": "admin123"},
        {"username": "admin", "password": "Admin123"},
        {"username": " admin ", "password": "admin123"},
        {"username": "admin", "password": " admin123 "},
    ]
    
    for i, case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f'{base_url}/api/login',
                json=case,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} Caso {i}: {case} → {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ Caso {i}: Error {e}")

if __name__ == "__main__":
    test_login_debug()
