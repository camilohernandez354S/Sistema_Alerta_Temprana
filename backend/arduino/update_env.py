"""
Función para actualizar el archivo .env preservando comentarios y otras variables
"""
import re
import os
from pathlib import Path

def actualizar_env(server_ip=None, flask_server_url=None, server_port=None, wifi_ssid=None, wifi_password=None):
    """
    Actualiza el archivo .env con nuevos valores, preservando comentarios y otras variables
    
    Args:
        server_ip: Nueva IP del servidor (opcional)
        flask_server_url: Nueva URL del servidor Flask (opcional)
        server_port: Puerto del servidor (opcional, usado para generar FLASK_SERVER_URL si no se proporciona)
        wifi_ssid: Nuevo SSID de WiFi (opcional)
        wifi_password: Nueva contraseña de WiFi (opcional)
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    # Detectar si estamos en Docker o localmente
    env_file = None
    
    # Primero intentar con /app/.env (Docker)
    if Path('/app/.env').exists():
        env_file = Path('/app/.env')
    else:
        # Buscar .env en el directorio raíz del proyecto (local)
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / '.env'
        
        if not env_file.exists():
            return False
    
    # Verificar permisos de escritura
    if not os.access(env_file, os.W_OK):
        print(f"⚠️  No se tienen permisos de escritura en {env_file}")
        return False
    
    try:
        # Leer el archivo completo
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Procesar cada línea
        updated = False
        new_lines = []
        
        for line in lines:
            original_line = line
            stripped = line.strip()
            
            # Si es un comentario o línea vacía, mantenerla tal cual
            if not stripped or stripped.startswith('#'):
                new_lines.append(original_line)
                continue
            
            # Buscar variables que necesitamos actualizar
            if server_ip and re.match(rf'^\s*SERVER_IP\s*=', line, re.IGNORECASE):
                # Actualizar SERVER_IP
                new_lines.append(f'SERVER_IP={server_ip}\n')
                updated = True
            elif flask_server_url and re.match(rf'^\s*FLASK_SERVER_URL\s*=', line, re.IGNORECASE):
                # Actualizar FLASK_SERVER_URL
                new_lines.append(f'FLASK_SERVER_URL={flask_server_url}\n')
                updated = True
            elif server_port and re.match(rf'^\s*SERVER_PORT\s*=', line, re.IGNORECASE):
                # Actualizar SERVER_PORT (solo si se proporciona)
                new_lines.append(f'SERVER_PORT={server_port}\n')
                updated = True
            elif wifi_ssid and re.match(rf'^\s*WIFI_SSID\s*=', line, re.IGNORECASE):
                # Actualizar WIFI_SSID
                new_lines.append(f'WIFI_SSID={wifi_ssid}\n')
                updated = True
            elif wifi_password and re.match(rf'^\s*WIFI_PASSWORD\s*=', line, re.IGNORECASE):
                # Actualizar WIFI_PASSWORD
                new_lines.append(f'WIFI_PASSWORD={wifi_password}\n')
                updated = True
            else:
                # Mantener la línea original
                new_lines.append(original_line)
        
        # Si se proporcionó server_ip pero no flask_server_url, generar la URL
        if server_ip and not flask_server_url and server_port:
            flask_server_url = f"http://{server_ip}:{server_port}"
            # Buscar si existe FLASK_SERVER_URL, si no, agregarlo después de SERVER_PORT
            flask_found = any(re.match(rf'^\s*FLASK_SERVER_URL\s*=', line, re.IGNORECASE) for line in lines)
            if not flask_found:
                # Agregar FLASK_SERVER_URL después de SERVER_PORT o al final
                insert_index = len(new_lines)
                for i, line in enumerate(new_lines):
                    if re.match(rf'^\s*SERVER_PORT\s*=', line, re.IGNORECASE):
                        insert_index = i + 1
                        break
                new_lines.insert(insert_index, f'FLASK_SERVER_URL={flask_server_url}\n')
                updated = True
        
        # Escribir el archivo actualizado
        if updated:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error al actualizar .env: {e}")
        return False

