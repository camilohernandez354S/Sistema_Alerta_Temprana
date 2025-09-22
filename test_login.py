#!/usr/bin/env python3
"""
Script para probar el login y diagnosticar problemas de conectividad
"""
import requests
import json

def test_backend_health():
    """Probar si el backend responde"""
    try:
        print("🔍 Probando conectividad con el backend...")
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        print(f"✅ Backend responde: {response.status_code}")
        print(f"📄 Respuesta: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al backend en localhost:5000")
        print("   ¿Está corriendo el servidor Flask?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout conectando al backend")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_login():
    """Probar el endpoint de login"""
    try:
        print("\n🔐 Probando login...")
        
        # Datos de login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        # Hacer petición
        response = requests.post(
            'http://localhost:5000/api/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Respuesta: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login exitoso!")
            return True
        else:
            print("❌ Login falló")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al endpoint de login")
        return False
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False

def test_cors():
    """Probar configuración CORS"""
    try:
        print("\n🌐 Probando CORS...")
        
        # Simular petición CORS preflight
        response = requests.options(
            'http://localhost:5000/api/login',
            headers={
                'Origin': 'http://localhost:8080',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=5
        )
        
        print(f"📊 CORS Status: {response.status_code}")
        print("📋 Headers CORS:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"   {header}: {value}")
                
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error probando CORS: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando diagnóstico del sistema de login...")
    print("=" * 50)
    
    # Probar conectividad básica
    if not test_backend_health():
        print("\n💡 Soluciones:")
        print("1. Verificar que el backend esté corriendo:")
        print("   cd backend/backend-flask")
        print("   python run.py")
        print("2. Verificar que el puerto 5000 esté libre")
        return
    
    # Probar CORS
    test_cors()
    
    # Probar login
    if test_login():
        print("\n🎉 ¡Todo funciona correctamente!")
    else:
        print("\n🔧 Revisar configuración del backend")
    
    print("\n" + "=" * 50)
    print("Diagnóstico completado")

if __name__ == "__main__":
    main()
