#!/usr/bin/env python3
"""
Script para generar ambos códigos QR automáticamente
- QR de WiFi (para conectar a la red)
- QR de URL (para acceder al sistema)
Obtiene la IP automáticamente desde el .env
"""
import sys
import subprocess
import socket
from pathlib import Path

# Agregar el directorio backend/arduino al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'arduino'))

try:
    from network_config import cargar_config_red
    import qrcode
except ImportError as e:
    print(f"Error: Falta instalar dependencias: {e}")
    print("Ejecuta: pip install qrcode[pil] python-dotenv")
    sys.exit(1)

def obtener_ip_red():
    """
    Obtiene la IP de la red local automáticamente
    """
    try:
        # Conectar a un servidor externo para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def generar_qr_wifi(config):
    """Genera QR de WiFi"""
    wifi_ssid = config.get('wifi_ssid', '')
    wifi_password = config.get('wifi_password', '')
    
    if not wifi_ssid:
        print("WIFI_SSID no configurado, omitiendo QR de WiFi")
        return False
    
    wifi_string = f"WIFI:T:WPA;S:{wifi_ssid};P:{wifi_password};;"
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(wifi_string)
    qr.make(fit=True)
    
    # Crear carpeta wifi si no existe
    # Detectar si estamos en Docker o localmente
    if Path('/qr_codes').exists():
        # Estamos en Docker
        qr_dir = Path('/qr_codes') / 'wifi'
    else:
        # Estamos localmente
        qr_dir = Path(__file__).parent.parent / 'qr_codes' / 'wifi'
    qr_dir.mkdir(parents=True, exist_ok=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    # Guardar archivo con el nombre de la red WiFi
    output_file = qr_dir / f'qr-wifi-{wifi_ssid}.png'
    img.save(output_file)
    
    print(f"QR WiFi: {output_file}")
    return True

def generar_qr_url(config):
    """Genera QR de URL"""
    server_ip = config.get('server_ip', '')
    frontend_port = config.get('frontend_port', '8080')
    
    # Si no hay IP en .env o es localhost, intentar obtenerla automáticamente
    if not server_ip or server_ip == 'localhost' or server_ip == '127.0.0.1':
        ip_auto = obtener_ip_red()
        if ip_auto:
            server_ip = ip_auto
            print(f"IP detectada automaticamente: {server_ip}")
        else:
            server_ip = 'localhost'
            print("No se pudo detectar IP automaticamente, usando localhost")
    
    url = f"http://{server_ip}:{frontend_port}"
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    
    # Crear carpeta url si no existe
    # Detectar si estamos en Docker o localmente
    if Path('/qr_codes').exists():
        # Estamos en Docker
        qr_dir = Path('/qr_codes') / 'url'
    else:
        # Estamos localmente
        qr_dir = Path(__file__).parent.parent / 'qr_codes' / 'url'
    qr_dir.mkdir(parents=True, exist_ok=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    # Guardar archivo con el nombre de la IP de la red
    ip_filename = server_ip.replace('.', '-')
    output_file = qr_dir / f'qr-url-{ip_filename}.png'
    img.save(output_file)
    
    print(f"QR URL: {output_file}")
    print(f"URL: {url}")
    return True

def generar_qrs_completos():
    """
    Genera ambos códigos QR automáticamente
    """
    try:
        # Configurar encoding para Windows
        import sys
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
        print("=" * 60)
        print("GENERANDO CODIGOS QR")
        print("=" * 60)
        print()
        
        # Cargar configuración del .env
        config = cargar_config_red()
        
        # Verificar IP en .env
        server_ip = config.get('server_ip', '')
        if not server_ip or server_ip == 'localhost':
            ip_auto = obtener_ip_red()
            if ip_auto:
                print(f"IP detectada automaticamente: {ip_auto}")
                print(f"Considera actualizar SERVER_IP={ip_auto} en tu .env")
                config['server_ip'] = ip_auto
        
        print()
        print("Generando QR codes...")
        print()
        
        # Generar QR de WiFi
        wifi_ok = generar_qr_wifi(config)
        
        # Generar QR de URL
        url_ok = generar_qr_url(config)
        
        print()
        print("=" * 60)
        if wifi_ok and url_ok:
            print("CODIGOS QR GENERADOS EXITOSAMENTE!")
        elif url_ok:
            print("QR de URL generado (QR de WiFi omitido)")
        else:
            print("Error al generar QR codes")
        print("=" * 60)
        print()
        print("Archivos guardados en:")
        print("   - qr_codes/wifi/qr-wifi.png (conectar a WiFi)")
        print("   - qr_codes/url/qr-url.png (acceder al sistema)")
        print()
        
        return wifi_ok and url_ok
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Crea un archivo .env en la raiz del proyecto")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    generar_qrs_completos()

