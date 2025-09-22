#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación Flask
"""
import os
from app import create_app
from app.factory import service_factory
from app.services.websocket_service import websocket_service

def main():
    """Función principal para ejecutar la aplicación"""
    # Obtener configuración del entorno
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Crear aplicación
    app = create_app(config_name)
    
    # Configurar cleanup al cerrar la aplicación
    @app.teardown_appcontext
    def cleanup_db(error):
        """Limpiar recursos al cerrar el contexto de la aplicación"""
        if error:
            app.logger.error(f"Error en el contexto de la aplicación: {error}")
    
    # Registrar cleanup al cerrar
    import atexit
    atexit.register(service_factory.cleanup)
    
    # Obtener configuración del puerto
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', False)
    
    app.logger.info(f"🚀 Iniciando aplicación en {host}:{port}")
    app.logger.info(f"🔧 Modo: {config_name}")
    app.logger.info(f"🐛 Debug: {'activado' if debug else 'desactivado'}")
    
    # Ejecutar aplicación con SocketIO
    try:
        if websocket_service.socketio:
            app.logger.info("🌐 Iniciando con WebSocket habilitado")
            websocket_service.socketio.run(
                app,
                host=host,
                port=port,
                debug=debug,
                use_reloader=debug,  # Solo usar reloader en desarrollo
                allow_unsafe_werkzeug=True  # Para desarrollo
            )
        else:
            app.logger.info("📡 Iniciando sin WebSocket")
            app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=debug,  # Solo usar reloader en desarrollo
                threaded=True
            )
    except KeyboardInterrupt:
        app.logger.info("👋 Aplicación detenida por el usuario")
    except Exception as e:
        app.logger.error(f"💥 Error ejecutando la aplicación: {e}")
    finally:
        app.logger.info("🛑 Cerrando aplicación...")

if __name__ == '__main__':
    main()
