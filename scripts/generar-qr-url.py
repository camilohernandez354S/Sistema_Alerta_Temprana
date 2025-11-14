#!/usr/bin/env python3
"""
Script para generar código QR de la URL del sistema
Lee la configuración del .env y genera un QR con la URL completa
Detecta automáticamente la IP de la red si no está en el .env
"""
import sys
import socket
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

def generar_qr_url():
    """
    Genera un código QR con la URL del sistema (frontend)
    Lee la IP del .env o la detecta automáticamente
    """
    try:
        # Configurar encoding para Windows
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
        # Cargar configuración del .env (forzar recarga)
        # Limpiar variables de entorno para forzar recarga
        import os
        for key in ['WIFI_SSID', 'WIFI_PASSWORD', 'SERVER_IP', 'SERVER_PORT', 'FRONTEND_PORT']:
            if key in os.environ:
                del os.environ[key]
        
        config = cargar_config_red()
        
        server_ip = config.get('server_ip', '').strip()
        frontend_port = config.get('frontend_port', '8080').strip()
        
        # Siempre intentar detectar la IP actual de la red para asegurar que sea la correcta
        ip_auto = obtener_ip_red()
        server_port = config.get('server_port', '5000').strip()
        
        if ip_auto and not ip_auto.startswith('172.'):  # Ignorar IPs de Docker
            # Usar la IP detectada automáticamente
            if server_ip != ip_auto:
                print(f"🔄 IP detectada automáticamente: {ip_auto}")
                print(f"   IP en .env: {server_ip}")
                print(f"   Actualizando .env con IP detectada...")
            
            server_ip = ip_auto
            flask_url = f"http://{ip_auto}:{server_port}"
            url = f"http://{ip_auto}:{frontend_port}"
            
            # Actualizar .env con la IP y URL detectadas
            if actualizar_env(server_ip=ip_auto, flask_server_url=flask_url, server_port=server_port):
                print(f"✅ .env actualizado automáticamente:")
                print(f"   SERVER_IP: {ip_auto}")
                print(f"   FLASK_SERVER_URL: {flask_url}")
            else:
                print("⚠️  No se pudo actualizar el .env")
        elif not server_ip or server_ip == 'localhost' or server_ip == '127.0.0.1':
            server_ip = 'localhost'
            print("⚠️  No se pudo detectar IP automáticamente, usando localhost")
            url = f"http://{server_ip}:{frontend_port}"
        else:
            # Construir URL completa con la IP del .env
            flask_url = f"http://{server_ip}:{server_port}"
            url = f"http://{server_ip}:{frontend_port}"
            
            # Actualizar FLASK_SERVER_URL si no está actualizado
            if actualizar_env(flask_server_url=flask_url, server_port=server_port):
                print(f"✅ .env actualizado con FLASK_SERVER_URL: {flask_url}")
        
        # Crear directorio para QR codes de URL si no existe
        # Detectar si estamos en Docker o localmente
        if Path('/qr_codes').exists():
            # Estamos en Docker
            qr_dir = Path('/qr_codes') / 'url'
        else:
            # Estamos localmente
            qr_dir = Path(__file__).parent.parent / 'qr_codes' / 'url'
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar archivo con el nombre de la IP de la red
        # Reemplazar puntos por guiones para el nombre de archivo
        ip_filename = server_ip.replace('.', '-')
        output_file = qr_dir / f'qr-url-{ip_filename}.png'
        img.save(output_file)
        
        print("=" * 60)
        print("CODIGO QR DE URL GENERADO")
        print("=" * 60)
        print(f"Archivo: {output_file}")
        print(f"URL: {url}")
        print()
        print("Escanea este QR con tu telefono para acceder al sistema")
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
    generar_qr_url()

