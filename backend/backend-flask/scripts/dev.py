#!/usr/bin/env python3
"""
Script de desarrollo para tareas comunes
"""
import os
import sys
import subprocess
from pathlib import Path

def run_app():
    """Ejecutar la aplicación en modo desarrollo"""
    os.environ['FLASK_ENV'] = 'development'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    print("🚀 Iniciando aplicación en modo desarrollo...")
    subprocess.run([sys.executable, 'run.py'])

def run_tests():
    """Ejecutar tests"""
    print("🧪 Ejecutando tests...")
    subprocess.run(['pytest', '-v', '--tb=short'])

def run_tests_coverage():
    """Ejecutar tests con cobertura"""
    print("📊 Ejecutando tests con cobertura...")
    subprocess.run(['pytest', '--cov=app', '--cov-report=html', '--cov-report=term'])

def lint_code():
    """Ejecutar linting"""
    print("🔍 Ejecutando linting...")
    subprocess.run(['flake8', 'app/'])

def format_code():
    """Formatear código"""
    print("✨ Formateando código...")
    subprocess.run(['black', 'app/'])
    subprocess.run(['isort', 'app/'])

def clean():
    """Limpiar archivos temporales"""
    print("🧹 Limpiando archivos temporales...")
    
    # Limpiar __pycache__
    for pycache in Path('.').rglob('__pycache__'):
        subprocess.run(['rm', '-rf', str(pycache)])
    
    # Limpiar .pyc files
    for pyc in Path('.').rglob('*.pyc'):
        pyc.unlink()
    
    print("✅ Limpieza completada")

def setup_dev():
    """Configurar entorno de desarrollo"""
    print("⚙️ Configurando entorno de desarrollo...")
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Copiar archivo de configuración si no existe
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            subprocess.run(['cp', 'env.example', '.env'])
            print("📝 Archivo .env creado desde env.example")
        else:
            print("⚠️ env.example no encontrado")
    
    print("✅ Configuración completada")

def install_deps():
    """Instalar dependencias"""
    print("📦 Instalando dependencias...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def help_menu():
    """Mostrar menú de ayuda"""
    print("""
🛠️ Script de Desarrollo - Sistema Arduino Nivel Agua

Comandos disponibles:
  run         Ejecutar aplicación en modo desarrollo
  test        Ejecutar tests
  test-cov    Ejecutar tests con cobertura
  lint        Ejecutar linting del código
  format      Formatear código con black e isort
  clean       Limpiar archivos temporales
  setup       Configurar entorno de desarrollo
  install     Instalar dependencias
  help        Mostrar esta ayuda

Uso: python scripts/dev.py <comando>
    """)

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        help_menu()
        return
    
    command = sys.argv[1]
    
    commands = {
        'run': run_app,
        'test': run_tests,
        'test-cov': run_tests_coverage,
        'lint': lint_code,
        'format': format_code,
        'clean': clean,
        'setup': setup_dev,
        'install': install_deps,
        'help': help_menu
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Comando '{command}' no reconocido")
        help_menu()

if __name__ == '__main__':
    main()
