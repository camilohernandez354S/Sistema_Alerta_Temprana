#!/usr/bin/env python3
"""
Script para resolver todos los conflictos de merge automáticamente
"""
import subprocess
import os

def run_git_command(command):
    """Ejecutar comando de git"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def resolve_conflicts():
    """Resolver todos los conflictos de merge"""
    print("🔧 Resolviendo conflictos de merge...")
    
    # Lista de archivos que queremos eliminar (fueron eliminados por la otra rama)
    files_to_remove = [
        # Cache files
        "backend/backend-flask/app/__pycache__/__init__.cpython-313.pyc",
        "backend/backend-flask/app/api/__pycache__/sensor_routes.cpython-313.pyc",
        "backend/backend-flask/app/controllers/__pycache__/sensor_controller.cpython-313.pyc",
        "backend/backend-flask/app/models/__pycache__/sensor_model.cpython-313.pyc",
        "backend/backend-flask/app/repositories/__pycache__/sensor_repository.cpython-313.pyc",
        "backend/backend-flask/app/services/__pycache__/prediction_service.cpython-313.pyc",
        "backend/backend-flask/app/services/__pycache__/sensor_service.cpython-313.pyc",
        "backend/backend-flask/app/utils/__pycache__/logging_config.cpython-313.pyc",
        "backend/backend-flask/config/__pycache__/config.cpython-313.pyc",
        
        # Source files that we don't need for basic functionality
        "backend/backend-flask/app/controllers/sensor_controller.py",
        "backend/backend-flask/app/models/sensor_model.py",
        "backend/backend-flask/app/repositories/sensor_repository.py",
        "backend/backend-flask/app/services/sensor_service.py",
        "backend/backend-flask/app/services/prediction_service.py",
        "backend/backend-flask/app/utils/logging_config.py",
        "backend/backend-flask/config/config.py",
        "backend/backend-flask/env.example",
        "backend/backend-flask/logs/app.log"
    ]
    
    # Remover archivos que no necesitamos
    removed_count = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            success, stdout, stderr = run_git_command(f'git rm "{file_path}"')
            if success:
                print(f"✅ Removido: {file_path}")
                removed_count += 1
            else:
                print(f"⚠️  No se pudo remover: {file_path}")
        else:
            # Si el archivo no existe, marcarlo como removido
            success, stdout, stderr = run_git_command(f'git rm --cached "{file_path}"')
            if success:
                print(f"✅ Marcado como removido: {file_path}")
                removed_count += 1
    
    print(f"\n📊 Archivos procesados: {removed_count}")
    
    # Agregar todos los archivos modificados
    print("\n📝 Agregando archivos modificados...")
    success, stdout, stderr = run_git_command('git add .')
    if success:
        print("✅ Archivos agregados al staging")
    else:
        print(f"❌ Error agregando archivos: {stderr}")
        return False
    
    return True

def check_merge_status():
    """Verificar el estado del merge"""
    success, stdout, stderr = run_git_command('git status --porcelain')
    if success:
        unmerged_files = [line for line in stdout.split('\n') if line.startswith('U')]
        if unmerged_files:
            print(f"⚠️  Quedan {len(unmerged_files)} archivos sin resolver:")
            for file_line in unmerged_files:
                print(f"   {file_line}")
            return False
        else:
            print("✅ Todos los conflictos resueltos")
            return True
    else:
        print(f"❌ Error verificando estado: {stderr}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando resolución automática de conflictos de merge")
    print("=" * 60)
    
    if resolve_conflicts():
        if check_merge_status():
            print("\n🎉 ¡Todos los conflictos resueltos exitosamente!")
            print("\n💡 Próximos pasos:")
            print("   1. git commit -m 'Resolve merge conflicts'")
            print("   2. cd backend/backend-flask")
            print("   3. python run.py")
        else:
            print("\n⚠️  Algunos conflictos aún necesitan resolución manual")
    else:
        print("\n❌ Error resolviendo conflictos")

if __name__ == "__main__":
    main()
