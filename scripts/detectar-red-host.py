"""
Script Python para detectar red WiFi y IP del host
Se ejecuta desde el host (no desde Docker) para acceder a comandos de Windows
"""
import subprocess
import sys
import re
from pathlib import Path

def detectar_ip_host():
    """Detecta la IP del host"""
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split('\n')
        
        for line in lines:
            # Buscar IPv4 que no sea Docker (172.x.x.x) ni localhost
            match = re.search(r'IPv4.*?:\s*(\d+\.\d+\.\d+\.\d+)', line)
            if match:
                ip = match.group(1)
                # Filtrar IPs de Docker y localhost
                if not ip.startswith('172.') and not ip.startswith('127.'):
                    return ip
    except Exception:
        pass
    return None

def detectar_red_wifi_host():
    """Detecta la red WiFi del host usando PowerShell"""
    try:
        # Ejecutar PowerShell para obtener la red WiFi
        ps_command = """
        $profile = Get-NetConnectionProfile -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -like '*Wi-Fi*' -or $_.InterfaceAlias -like '*WLAN*' } | Select-Object -First 1
        if ($profile -and $profile.Name) {
            Write-Output $profile.Name.Trim()
        }
        """
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    
    # Fallback: usar netsh
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if 'SSID' in line and 'BSSID' not in line and 'Nombre' not in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    ssid = match.group(1).strip()
                    if ssid and ssid.lower() != 'none':
                        return ssid
    except Exception:
        pass
    
    return None

def obtener_password_wifi(ssid):
    """Intenta obtener la contraseña WiFi del perfil guardado"""
    try:
        ps_command = f"""
        $output = netsh wlan show profile name="{ssid}" key=clear 2>&1 | Out-String
        if ($output -match 'Contenido de la clave\\s*:\\s*(.+)' -or $output -match 'Key Content\\s*:\\s*(.+)') {{
            Write-Output $matches[1].Trim()
        }}
        """
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    
    return None

def actualizar_env(ip=None, wifi_ssid=None, wifi_password=None):
    """Actualiza el archivo .env con los valores detectados"""
    # Buscar .env en la raíz del proyecto
    project_root = Path(__file__).parent.parent
    env_file = project_root / '.env'
    
    if not env_file.exists():
        print(f"❌ No se encontró .env en: {env_file}")
        return False
    
    try:
        # Leer el archivo
        lines = env_file.read_text(encoding='utf-8').split('\n')
        new_lines = []
        updated = False
        
        for line in lines:
            original = line
            
            # Actualizar SERVER_IP
            if ip and re.match(r'^\s*SERVER_IP\s*=', line, re.IGNORECASE):
                new_lines.append(f'SERVER_IP={ip}\n')
                updated = True
            # Actualizar FLASK_SERVER_URL
            elif ip and re.match(r'^\s*FLASK_SERVER_URL\s*=', line, re.IGNORECASE):
                new_lines.append(f'FLASK_SERVER_URL=http://{ip}:5000\n')
                updated = True
            # Actualizar WIFI_SSID
            elif wifi_ssid and re.match(r'^\s*WIFI_SSID\s*=', line, re.IGNORECASE):
                new_lines.append(f'WIFI_SSID={wifi_ssid}\n')
                updated = True
            # Actualizar WIFI_PASSWORD
            elif wifi_password and re.match(r'^\s*WIFI_PASSWORD\s*=', line, re.IGNORECASE):
                new_lines.append(f'WIFI_PASSWORD={wifi_password}\n')
                updated = True
            else:
                new_lines.append(original + '\n' if not original.endswith('\n') else original)
        
        # Escribir el archivo actualizado
        if updated:
            env_file.write_text(''.join(new_lines), encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        print(f"❌ Error al actualizar .env: {e}")
        return False

if __name__ == '__main__':
    import sys
    
    # Configurar encoding para Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    ejecutar_docker_compose = '--rebuild' in sys.argv
    
    print("🔄 Detectando configuración de red del host...")
    print()
    
    # Detectar IP
    ip = detectar_ip_host()
    if ip:
        print(f"✅ IP detectada: {ip}")
    else:
        print("⚠️  No se pudo detectar IP")
    
    # Detectar red WiFi
    wifi_ssid = detectar_red_wifi_host()
    if wifi_ssid:
        print(f"✅ Red WiFi detectada: {wifi_ssid}")
    else:
        print("⚠️  No se pudo detectar red WiFi")
    
    # Obtener contraseña WiFi
    wifi_password = None
    if wifi_ssid:
        wifi_password = obtener_password_wifi(wifi_ssid)
        if wifi_password:
            print(f"✅ Contraseña WiFi obtenida")
        else:
            print("⚠️  No se pudo obtener contraseña WiFi automáticamente")
    
    # Actualizar .env
    actualizado = False
    if ip or wifi_ssid or wifi_password:
        if actualizar_env(ip=ip, wifi_ssid=wifi_ssid, wifi_password=wifi_password):
            print("✅ .env actualizado correctamente")
            actualizado = True
        else:
            print("⚠️  No se pudo actualizar .env")
    else:
        print("⚠️  No hay información para actualizar")
    
    # Si se actualizó y se solicitó rebuild, ejecutar docker compose
    if actualizado and ejecutar_docker_compose:
        print()
        print("🔄 Reiniciando contenedores con nueva configuración...")
        try:
            result = subprocess.run(
                ['docker', 'compose', 'up', '-d', '--build'],
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                print("✅ Contenedores reiniciados correctamente")
            else:
                print(f"⚠️  Error al reiniciar contenedores: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Error al ejecutar docker compose: {e}")

