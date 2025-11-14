"""
Script para generar configuración WiFi para Arduino ESP8266/ESP32
Lee las credenciales del archivo .env y genera un archivo de configuración
"""
from pathlib import Path
from network_config import cargar_config_red, validar_config_red, obtener_url_servidor

def generar_config_wifi():
    """
    Genera el archivo wifi_config.h con las credenciales WiFi del .env
    """
    try:
        # Cargar configuración de red
        config = cargar_config_red()
        
        # Validar configuración
        es_valida, errores = validar_config_red()
        if not es_valida:
            print("❌ Errores en la configuración:")
            for error in errores:
                print(f"   - {error}")
            print("\n💡 Edita el archivo .env y agrega las variables faltantes")
            return False
        
        wifi_ssid = config['wifi_ssid']
        wifi_password = config['wifi_password']
        flask_server_url = config.get('flask_server_url', '')
        
        if not wifi_ssid:
            print("❌ WIFI_SSID no está configurado en el archivo .env")
            print("💡 Agrega WIFI_SSID=nombre_de_tu_red al archivo .env")
            return False
        
        if not wifi_password:
            print("⚠️  WIFI_PASSWORD no está configurado en el archivo .env")
            print("💡 Agrega WIFI_PASSWORD=tu_contraseña al archivo .env")
            print("   (Puede estar vacío si la red no tiene contraseña)")
        
        # Parsear URL del servidor
        import re
        from urllib.parse import urlparse
        
        if flask_server_url:
            parsed = urlparse(flask_server_url)
            server_host = parsed.hostname or config.get('server_ip', 'localhost')
            server_port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            use_https = parsed.scheme == 'https'
            server_path = parsed.path.rstrip('/') or ''
        else:
            # Fallback a configuración antigua
            server_host = config.get('server_ip', 'localhost')
            server_port = config.get('server_port', '5000')
            use_https = False
            server_path = ''
        
        # Generar archivo de configuración
        protocolo_str = "https" if use_https else "http"
        config_content = f"""/*
 * Configuración WiFi generada automáticamente
 * Este archivo se genera desde generar_config_wifi.py
 * NO editar manualmente - se sobrescribirá al ejecutar el script
 */

#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

// Credenciales WiFi
#define WIFI_SSID "{wifi_ssid}"
#define WIFI_PASSWORD "{wifi_password}"

// Configuración del servidor Flask
#define SERVER_HOST "{server_host}"
#define SERVER_PORT {server_port}
#define SERVER_PATH "{server_path}"
#define USE_HTTPS {1 if use_https else 0}
#define SERVER_PROTOCOL "{protocolo_str}"

// Configuración de reintentos
#define WIFI_MAX_RETRIES 20
#define WIFI_RETRY_DELAY 500  // milisegundos

#endif // WIFI_CONFIG_H
"""
        
        # Escribir archivo
        config_file = Path(__file__).parent / 'wifi_config.h'
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✅ Archivo wifi_config.h generado correctamente")
        print()
        print("📋 Configuración aplicada desde .env:")
        print(f"   WiFi SSID:        {wifi_ssid}")
        print(f"   WiFi Password:    {'*' * len(wifi_password) if wifi_password else '(vacío)'}")
        print(f"   Servidor:         {protocolo_str}://{server_host}:{server_port}{server_path}")
        print(f"   HTTPS:            {'Sí' if use_https else 'No'}")
        print()
        print(f"📁 Archivo generado: {config_file}")
        print()
        print("💡 Próximo paso: Sube el código nivel_agua_wifi.ino al Arduino")
        
        return True
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Crea un archivo .env en la raíz del proyecto")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == '__main__':
    generar_config_wifi()
