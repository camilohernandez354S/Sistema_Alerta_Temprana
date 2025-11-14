"""
Módulo de configuración de red centralizado
Lee la configuración del .env y proporciona funciones para generar configuraciones
tanto para el servidor Flask como para el Arduino WiFi
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def cargar_config_red():
    """
    Carga la configuración de red desde el archivo .env
    
    Returns:
        dict: Diccionario con la configuración de red
    """
    # Buscar .env en el directorio raíz del proyecto
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / '.env'
    
    if not env_file.exists():
        # Intentar con example.env
        env_file = project_root / 'config' / 'example.env'
        if not env_file.exists():
            raise FileNotFoundError("No se encontró archivo .env")
    
    load_dotenv(env_file)
    
    config = {
        'server_ip': os.getenv('SERVER_IP', '192.168.137.24'),
        'server_port': os.getenv('SERVER_PORT', '5000'),
        'frontend_port': os.getenv('FRONTEND_PORT', '8080'),
        'wifi_ssid': os.getenv('WIFI_SSID', ''),
        'wifi_password': os.getenv('WIFI_PASSWORD', ''),
        'flask_server_url': os.getenv('FLASK_SERVER_URL', '')
    }
    
    # Generar FLASK_SERVER_URL si no está definido
    if not config['flask_server_url']:
        config['flask_server_url'] = f"http://{config['server_ip']}:{config['server_port']}"
    
    return config

def obtener_url_servidor():
    """
    Obtiene la URL completa del servidor Flask
    
    Returns:
        str: URL del servidor Flask
    """
    config = cargar_config_red()
    return config['flask_server_url']

def obtener_ip_servidor():
    """
    Obtiene la IP del servidor
    
    Returns:
        str: IP del servidor
    """
    config = cargar_config_red()
    return config['server_ip']

def obtener_credenciales_wifi():
    """
    Obtiene las credenciales WiFi
    
    Returns:
        tuple: (SSID, PASSWORD)
    """
    config = cargar_config_red()
    return config['wifi_ssid'], config['wifi_password']

def validar_config_red():
    """
    Valida que la configuración de red esté completa
    
    Returns:
        tuple: (bool, list) - (es_válida, lista_de_errores)
    """
    errores = []
    config = cargar_config_red()
    
    if not config['server_ip']:
        errores.append("SERVER_IP no está configurado")
    
    if not config['server_port']:
        errores.append("SERVER_PORT no está configurado")
    
    if not config['wifi_ssid']:
        errores.append("WIFI_SSID no está configurado (requerido para Arduino WiFi)")
    
    return len(errores) == 0, errores

def mostrar_config_red():
    """
    Muestra la configuración de red actual
    """
    try:
        config = cargar_config_red()
        print("=" * 50)
        print("CONFIGURACIÓN DE RED")
        print("=" * 50)
        print(f"IP del Servidor:     {config['server_ip']}")
        print(f"Puerto Backend:       {config['server_port']}")
        print(f"Puerto Frontend:      {config['frontend_port']}")
        print(f"URL Servidor Flask:   {config['flask_server_url']}")
        print(f"URL Frontend:         http://{config['server_ip']}:{config['frontend_port']}")
        print()
        print("CONFIGURACIÓN WiFi (Arduino)")
        print("-" * 50)
        print(f"SSID:                 {config['wifi_ssid'] or '(no configurado)'}")
        print(f"Contraseña:           {'*' * len(config['wifi_password']) if config['wifi_password'] else '(no configurado)'}")
        print("=" * 50)
        
        # Validar configuración
        es_valida, errores = validar_config_red()
        if not es_valida:
            print("\n⚠️  ADVERTENCIAS:")
            for error in errores:
                print(f"   - {error}")
        else:
            print("\n✅ Configuración válida")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Crea un archivo .env en la raíz del proyecto")

if __name__ == '__main__':
    mostrar_config_red()

