#!/usr/bin/env python3
"""
Script para generar código QR de WiFi
Lee las credenciales del .env y genera un QR que permite conectar automáticamente
"""
import sys
import os
from pathlib import Path

# Agregar el directorio backend/arduino al path para importar network_config
# Detectar si estamos en Docker o localmente
if Path('/scripts').exists() and Path(__file__).parent == Path('/scripts'):
    # Estamos en Docker, usar ruta absoluta
    sys.path.insert(0, '/app/../arduino')
else:
    # Estamos localmente, usar ruta relativa
    sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'arduino'))

try:
    from network_config import cargar_config_red
    from update_env import actualizar_env
    import qrcode
    from qrcode.image.pil import PilImage
    import socket
except ImportError as e:
    print(f"❌ Error: Falta instalar dependencias: {e}")
    print("💡 Ejecuta: pip install qrcode[pil] python-dotenv")
    sys.exit(1)

def obtener_ip_red():
    """
    Obtiene la IP de la red local automáticamente
    """
    try:
        # Conectar a un servidor externo para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return None

def obtener_red_wifi_actual():
    """
    Detecta la red WiFi a la que está conectado actualmente
    Funciona en Windows y Linux
    Si está en Docker, ejecuta un script PowerShell en el host
    """
    import subprocess
    import platform
    
    try:
        # Detectar si estamos en Docker
        en_docker = Path('/scripts').exists() and Path(__file__).parent == Path('/scripts')
        
        if en_docker:
            # Estamos en Docker, ejecutar script PowerShell en el host
            # El script está montado en /scripts, pero necesitamos ejecutarlo en el host
            # Usar docker exec para ejecutar en el host o leer desde archivo compartido
            try:
                # Intentar leer desde archivo temporal compartido
                temp_file = Path('/app/../temp/red_wifi_actual.txt')
                if temp_file.exists():
                    ssid = temp_file.read_text(encoding='utf-8').strip()
                    if ssid:
                        return ssid
            except:
                pass
            
            # Si no hay archivo, intentar ejecutar el script desde el host
            # Esto requiere que el script esté disponible en el host
            return None
        
        # Estamos en el host, ejecutar directamente
        if platform.system() == 'Windows':
            # En Windows, intentar primero con PowerShell script (más confiable)
            try:
                script_path = Path(__file__).parent / 'detectar-red-wifi.ps1'
                if script_path.exists():
                    result = subprocess.run(
                        ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        timeout=5
                    )
                    if result.returncode == 0:
                        ssid = result.stdout.strip()
                        if ssid:
                            return ssid
            except Exception as e:
                pass
            
            # Si PowerShell falla, usar netsh directamente
            try:
                result = subprocess.run(
                    ['netsh', 'wlan', 'show', 'interfaces'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=5
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'SSID' in line and 'BSSID' not in line and 'Nombre' not in line.lower():
                            # Formato: "SSID                   : NombreRed"
                            parts = line.split(':')
                            if len(parts) > 1:
                                ssid = parts[1].strip()
                                if ssid and ssid != '' and ssid.lower() != 'none':
                                    return ssid
            except Exception as e:
                pass
        else:
            # En Linux, usar nmcli o iwgetid
            try:
                result = subprocess.run(
                    ['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if ':yes:' in line or line.startswith('yes:'):
                            parts = line.split(':')
                            if len(parts) > 1:
                                ssid = parts[-1].strip()
                                if ssid:
                                    return ssid
            except:
                # Intentar con iwgetid
                try:
                    result = subprocess.run(
                        ['iwgetid', '-r'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        ssid = result.stdout.strip()
                        if ssid:
                            return ssid
                except:
                    pass
    except Exception as e:
        print(f"⚠️  Error al detectar red WiFi: {e}")
    
    return None

def ejecutar_actualizacion_host():
    """
    Ejecuta el script PowerShell generar-qr-completo-host.ps1 en el host desde Docker
    Detecta red WiFi, IP y contraseña, actualiza .env y reinicia contenedores
    """
    import subprocess
    import os
    
    try:
        # El script PowerShell está en /scripts/generar-qr-completo-host.ps1
        script_path = Path('/scripts/generar-qr-completo-host.ps1')
        
        if not script_path.exists():
            print(f"⚠️  No se encontró el script: {script_path}")
            return False
        
        # Obtener la ruta absoluta del proyecto en el host
        # Desde /app/.env sabemos que el .env está en la raíz
        # El script está en /scripts que corresponde a ./scripts en la raíz
        project_root = Path('/app').parent.parent
        
        print("🔄 Ejecutando detección y actualización en el host...")
        print()
        
        # Ejecutar PowerShell en el host usando docker run
        # Montamos el directorio del proyecto y el socket de Docker
        # Usamos PowerShell de Microsoft para ejecutar el script
        result = subprocess.run(
            ['docker', 'run', '--rm',
             '-v', '/var/run/docker.sock:/var/run/docker.sock',  # Socket de Docker
             '-v', f'{project_root}:/workspace:rw',  # Montar el proyecto completo
             '-w', '/workspace',
             'mcr.microsoft.com/powershell:latest',
             'pwsh', '-ExecutionPolicy', 'Bypass', '-File', 'scripts/generar-qr-completo-host.ps1'],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos para docker compose up -d --build
            env=os.environ.copy()
        )
        
        # Mostrar salida del script
        if result.stdout:
            try:
                output = result.stdout
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='replace')
                print(output)
            except:
                print(result.stdout)
        
        if result.stderr:
            stderr = result.stderr
            if isinstance(stderr, bytes):
                stderr = stderr.decode('utf-8', errors='replace')
            # Mostrar errores
            if result.returncode != 0:
                print(f"⚠️  {stderr}")
            else:
                # A veces PowerShell escribe a stderr pero es exitoso
                if 'Warning' not in stderr and 'Error' not in stderr:
                    pass  # Ignorar warnings menores
        
        return result.returncode == 0
        
    except FileNotFoundError:
        # Docker no está disponible en el contenedor
        print("⚠️  Docker no disponible en el contenedor")
        print("💡 Ejecuta manualmente: powershell -ExecutionPolicy Bypass -File scripts/generar-qr-completo-host.ps1")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Tiempo de espera agotado al ejecutar el script")
        return False
    except Exception as e:
        print(f"⚠️  Error al actualizar desde host: {e}")
        return False

def generar_qr_wifi():
    """
    Genera un código QR para conectar a la red WiFi automáticamente
    Formato: WIFI:T:WPA;S:SSID;P:PASSWORD;;
    Lee las credenciales del archivo .env
    Actualiza automáticamente el .env con IP y red WiFi del host
    """
    try:
        # Configurar encoding para Windows
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
        # Detectar si estamos en Docker y actualizar .env desde el host
        en_docker = Path('/scripts').exists() and Path(__file__).parent == Path('/scripts')
        if en_docker:
            print("=" * 60)
            print("DETECTANDO CONFIGURACIÓN DE RED DEL HOST")
            print("=" * 60)
            print()
            if ejecutar_actualizacion_host():
                print()
                print("✅ Configuración actualizada y contenedores reiniciados")
                print("💡 Espera unos segundos para que los contenedores se reinicien...")
                print()
            else:
                print()
                print("⚠️  No se pudo actualizar desde el host, usando .env actual")
                print()
        
        # Cargar configuración del .env (forzar recarga)
        # Limpiar variables de entorno para forzar recarga
        import os
        for key in ['WIFI_SSID', 'WIFI_PASSWORD', 'SERVER_IP', 'SERVER_PORT', 'FRONTEND_PORT', 'FLASK_SERVER_URL']:
            if key in os.environ:
                del os.environ[key]
        
        # Forzar recarga del .env
        config = cargar_config_red()
        
        wifi_ssid = config.get('wifi_ssid', '').strip()
        wifi_password = config.get('wifi_password', '').strip()
        server_port = config.get('server_port', '5000').strip()
        server_ip_actual = config.get('server_ip', '').strip()
        
        # Detectar red WiFi actual
        red_actual = obtener_red_wifi_actual()
        
        print(f"📋 Valores leídos del .env:")
        print(f"   WIFI_SSID: {wifi_ssid}")
        print(f"   SERVER_IP: {server_ip_actual}")
        if red_actual:
            print(f"   Red WiFi detectada: {red_actual}")
        print()
        
        # Si se detectó una red WiFi, actualizar el .env automáticamente
        if red_actual:
            if red_actual != wifi_ssid:
                print(f"🔄 Red WiFi detectada ({red_actual}) diferente a la del .env ({wifi_ssid})")
                print(f"   Actualizando .env automáticamente con la red detectada...")
            else:
                print(f"✅ Red WiFi detectada ({red_actual}) coincide con el .env")
            
            # Siempre actualizar para asegurar que esté sincronizado
            if actualizar_env(wifi_ssid=red_actual):
                print(f"✅ .env actualizado automáticamente con WIFI_SSID: {red_actual}")
                wifi_ssid = red_actual
                # Recargar configuración después de actualizar
                for key in ['WIFI_SSID', 'WIFI_PASSWORD', 'SERVER_IP', 'SERVER_PORT', 'FRONTEND_PORT', 'FLASK_SERVER_URL']:
                    if key in os.environ:
                        del os.environ[key]
                config = cargar_config_red()
                wifi_password = config.get('wifi_password', '').strip()
            else:
                print("⚠️  No se pudo actualizar el .env, usando red del .env")
        else:
            print("⚠️  No se pudo detectar la red WiFi actual, usando la del .env")
            print("💡 Asegúrate de estar conectado a una red WiFi")
        
        if not wifi_ssid:
            print("❌ WIFI_SSID no está configurado en el archivo .env")
            return False
        
        # Detectar IP del host (no del contenedor Docker)
        ip_auto = obtener_ip_red()
        
        if ip_auto and not ip_auto.startswith('172.'):  # Ignorar IPs de Docker
            # Actualizar .env con la IP detectada
            if server_ip_actual != ip_auto:
                print(f"🔄 IP detectada automáticamente: {ip_auto}")
                print(f"   IP en .env: {server_ip_actual}")
                print(f"   Actualizando .env con IP detectada...")
            
            flask_url = f"http://{ip_auto}:{server_port}"
            if actualizar_env(server_ip=ip_auto, flask_server_url=flask_url, server_port=server_port):
                print(f"✅ .env actualizado automáticamente:")
                print(f"   SERVER_IP: {ip_auto}")
                print(f"   FLASK_SERVER_URL: {flask_url}")
            else:
                print("⚠️  No se pudo actualizar el .env")
        
        # Crear formato WiFi QR (estándar WIFI:)
        # Formato: WIFI:T:TIPO;S:SSID;P:PASSWORD;;
        wifi_string = f"WIFI:T:WPA;S:{wifi_ssid};P:{wifi_password};;"
        
        # Crear directorio para QR codes de WiFi si no existe
        # Detectar si estamos en Docker o localmente
        if Path('/qr_codes').exists():
            # Estamos en Docker
            qr_dir = Path('/qr_codes') / 'wifi'
        else:
            # Estamos localmente
            qr_dir = Path(__file__).parent.parent / 'qr_codes' / 'wifi'
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(wifi_string)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar archivo con el nombre de la red WiFi
        output_file = qr_dir / f'qr-wifi-{wifi_ssid}.png'
        img.save(output_file)
        
        print("=" * 60)
        print("CODIGO QR DE WIFI GENERADO")
        print("=" * 60)
        print(f"Archivo: {output_file}")
        print(f"Red WiFi: {wifi_ssid}")
        print(f"Contrasena: {'*' * len(wifi_password) if wifi_password else '(sin contrasena)'}")
        print()
        print("Escanea este QR con tu telefono para conectarte automaticamente a la red WiFi")
        print("=" * 60)
        
        return True
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Crea un archivo .env en la raiz del proyecto")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

if __name__ == '__main__':
    generar_qr_wifi()

