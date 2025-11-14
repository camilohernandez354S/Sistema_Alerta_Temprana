"""
Servicio WebSocket para comunicación en tiempo real
"""
from flask_socketio import SocketIO, emit
from flask import request

class WebSocketService:
    """Servicio WebSocket para comunicación en tiempo real"""
    
    def __init__(self):
        self.socketio = None
    
    def init_app(self, app):
        """Inicializar SocketIO con la aplicación Flask"""
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        @self.socketio.on('connect')
        def handle_connect():
            """Manejar conexión de cliente"""
            app.logger.info(f'Cliente conectado: {request.sid}')
            emit('status', {'message': 'Conectado al servidor', 'connected': True})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Manejar desconexión de cliente"""
            app.logger.info(f'Cliente desconectado: {request.sid}')
        
        @self.socketio.on('ping')
        def handle_ping():
            """Manejar ping de cliente"""
            emit('pong', {'timestamp': None})
        
        app.logger.info('✅ WebSocket service inicializado correctamente')
    
    def emit_medicion(self, data):
        """Emitir nueva medición a todos los clientes conectados"""
        if self.socketio:
            self.socketio.emit('nueva_medicion', data, namespace='/', broadcast=True)
            return True
        return False
    
    def emit_estado(self, data):
        """Emitir cambio de estado a todos los clientes conectados"""
        if self.socketio:
            self.socketio.emit('cambio_estado', data, namespace='/', broadcast=True)
            return True
        return False
    
    def run(self, app, **kwargs):
        """Ejecutar servidor con SocketIO"""
        if self.socketio:
            return self.socketio.run(app, **kwargs)
        else:
            return app.run(**kwargs)

# Instancia global del servicio
websocket_service = WebSocketService()
