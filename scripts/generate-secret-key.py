#!/usr/bin/env python3
"""
Generador de SECRET_KEY segura para Flask
Genera claves aleatorias seguras usando diferentes métodos
"""

import secrets
import string
import os
from datetime import datetime

def generate_secret_key_method1():
    """Método 1: Usando secrets.token_hex() - Recomendado"""
    return secrets.token_hex(32)

def generate_secret_key_method2():
    """Método 2: Usando secrets.token_urlsafe()"""
    return secrets.token_urlsafe(32)

def generate_secret_key_method3():
    """Método 3: Combinando caracteres aleatorios"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(64))

def generate_secret_key_method4():
    """Método 4: Usando os.urandom()"""
    return os.urandom(32).hex()

def main():
    print("=" * 60)
    print("🔐 GENERADOR DE SECRET_KEY SEGURA")
    print("=" * 60)
    print()
    
    print("📋 MÉTODOS DISPONIBLES:")
    print("1. secrets.token_hex(32) - RECOMENDADO")
    print("2. secrets.token_urlsafe(32)")
    print("3. Caracteres aleatorios personalizados")
    print("4. os.urandom(32).hex()")
    print("5. Generar todas las opciones")
    print()
    
    choice = input("Selecciona un método [1-5]: ").strip()
    
    print("\n" + "=" * 60)
    print("🔑 SECRET_KEY GENERADA:")
    print("=" * 60)
    
    if choice == "1":
        key = generate_secret_key_method1()
        print(f"SECRET_KEY={key}")
        print("\n✅ Método recomendado: secrets.token_hex(32)")
        
    elif choice == "2":
        key = generate_secret_key_method2()
        print(f"SECRET_KEY={key}")
        print("\n✅ Método alternativo: secrets.token_urlsafe(32)")
        
    elif choice == "3":
        key = generate_secret_key_method3()
        print(f"SECRET_KEY={key}")
        print("\n✅ Método personalizado: caracteres aleatorios")
        
    elif choice == "4":
        key = generate_secret_key_method4()
        print(f"SECRET_KEY={key}")
        print("\n✅ Método sistema: os.urandom(32).hex()")
        
    elif choice == "5":
        print("🔑 TODAS LAS OPCIONES:")
        print()
        print("1. RECOMENDADO:")
        print(f"   SECRET_KEY={generate_secret_key_method1()}")
        print()
        print("2. ALTERNATIVO:")
        print(f"   SECRET_KEY={generate_secret_key_method2()}")
        print()
        print("3. PERSONALIZADO:")
        print(f"   SECRET_KEY={generate_secret_key_method3()}")
        print()
        print("4. SISTEMA:")
        print(f"   SECRET_KEY={generate_secret_key_method4()}")
        
    else:
        print("❌ Opción inválida")
        return
    
    print("\n" + "=" * 60)
    print("📝 INSTRUCCIONES:")
    print("=" * 60)
    print("1. Copia la SECRET_KEY generada")
    print("2. En Render.com, ve a tu servicio backend")
    print("3. Ve a 'Environment' → 'Environment Variables'")
    print("4. Agrega: SECRET_KEY = [tu_clave_generada]")
    print("5. Guarda y redespliega")
    print()
    print("⚠️  IMPORTANTE:")
    print("- NUNCA compartas tu SECRET_KEY")
    print("- Úsala SOLO en producción")
    print("- Para desarrollo local usa una clave diferente")
    print()
    print(f"🕒 Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
