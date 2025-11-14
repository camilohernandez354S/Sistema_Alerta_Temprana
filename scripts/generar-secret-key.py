#!/usr/bin/env python3
"""
Script para generar una clave secreta segura para Flask
"""

import secrets

def generar_secret_key():
    """Genera una clave secreta segura de 64 caracteres"""
    return secrets.token_hex(32)

if __name__ == '__main__':
    key = generar_secret_key()
    print("=" * 60)
    print("CLAVE SECRETA GENERADA PARA FLASK")
    print("=" * 60)
    print()
    print(f"SECRET_KEY={key}")
    print()
    print("💡 Copia esta línea y agrégala a:")
    print("   - Tu archivo .env local")
    print("   - Variables de entorno en Render (sat-backend)")
    print()
    print("⚠️  IMPORTANTE: No compartas esta clave públicamente")
    print("=" * 60)

