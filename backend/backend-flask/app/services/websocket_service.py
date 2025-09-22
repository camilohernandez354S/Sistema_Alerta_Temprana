"""
Servicio WebSocket básico para compatibilidad
"""

class WebSocketService:
    """Servicio WebSocket básico"""
    
    def __init__(self):
        self.socketio = None
    
    def init_app(self, app):
        """Inicializar con la aplicación Flask"""
        pass

# Instancia global del servicio
websocket_service = WebSocketService()
