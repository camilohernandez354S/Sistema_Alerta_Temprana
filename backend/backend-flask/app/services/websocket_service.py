"""
Servicio para comunicación WebSocket en tiempo real
"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import current_app, request
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

class WebSocketService:
    """Servicio para manejo de WebSocket"""
    
    def __init__(self):
        """Inicializar servicio WebSocket"""
        self.socketio: Optional[SocketIO] = None
        self.connected_users: Dict[str, str] = {}  # user_id -> session_id
        self.room_users: Dict[str, set] = {  # room -> set of user_ids
            'admin': set(),
            'operator': set(),
            'public': set()
        }
        self._logger = logging.getLogger(__name__)
        self._logger.info("WebSocketService inicializado")
    
    def _log(self, level: str, message: str):
        """
        Método helper para logging que funciona con o sin contexto de Flask
        
        Args:
            level: Nivel de log (info, warning, error, debug)
            message: Mensaje a loggear
        """
        try:
            # Intentar usar el logger de Flask si está disponible
            flask_logger = current_app.logger
            getattr(flask_logger, level)(message)
        except RuntimeError:
            # Si no hay contexto de Flask, usar el logger estándar
            getattr(self._logger, level)(message)
    
    def init_app(self, app):
        """Inicializar SocketIO con la aplicación Flask"""
        self.socketio = SocketIO(
            app,
            cors_allowed_origins=app.config.get('CORS_ORIGINS', ['http://localhost:8080']),
            logger=True,
            engineio_logger=True
        )
        
        # Registrar eventos
        self._register_events()
        self._log("info", "SocketIO inicializado")
    
    def _register_events(self):
        """Registrar eventos de WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Manejar conexión de cliente"""
            self._log("info", f"Cliente conectado: {request.sid}")
            emit('connected', {'message': 'Conectado al servidor', 'timestamp': datetime.utcnow().isoformat()})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Manejar desconexión de cliente"""
            self._log("info", f"Cliente desconectado: {request.sid}")
            
            # Remover usuario de todas las salas
            for room, users in self.room_users.items():
                if request.sid in users:
                    users.remove(request.sid)
                    leave_room(room)
            
            # Remover de usuarios conectados
            user_id = None
            for uid, sid in self.connected_users.items():
                if sid == request.sid:
                    user_id = uid
                    break
            
            if user_id:
                del self.connected_users[user_id]
                emit('user_disconnected', {'user_id': user_id}, broadcast=True)
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Manejar unirse a una sala"""
            try:
                room = data.get('room', 'public')
                user_id = data.get('user_id')
                
                if room not in self.room_users:
                    self.room_users[room] = set()
                
                # Unirse a la sala
                join_room(room)
                self.room_users[room].add(request.sid)
                
                if user_id:
                    self.connected_users[user_id] = request.sid
                
                self._log("info", f"Usuario {user_id} se unió a la sala {room}")
                emit('joined_room', {
                    'room': room,
                    'user_id': user_id,
                    'message': f'Te uniste a la sala {room}'
                })
                
                # Notificar a otros usuarios
                emit('user_joined', {
                    'user_id': user_id,
                    'room': room
                }, room=room, include_self=False)
                
            except Exception as e:
                self._log("error", f"Error uniéndose a sala: {e}")
                emit('error', {'message': 'Error uniéndose a la sala'})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Manejar salir de una sala"""
            try:
                room = data.get('room', 'public')
                user_id = data.get('user_id')
                
                # Salir de la sala
                leave_room(room)
                if room in self.room_users:
                    self.room_users[room].discard(request.sid)
                
                self._log("info", f"Usuario {user_id} salió de la sala {room}")
                emit('left_room', {
                    'room': room,
                    'user_id': user_id,
                    'message': f'Saliste de la sala {room}'
                })
                
                # Notificar a otros usuarios
                emit('user_left', {
                    'user_id': user_id,
                    'room': room
                }, room=room, include_self=False)
                
            except Exception as e:
                self._log("error", f"Error saliendo de sala: {e}")
                emit('error', {'message': 'Error saliendo de la sala'})
        
        @self.socketio.on('sensor_data_update')
        def handle_sensor_data(data):
            """Manejar actualización de datos de sensor"""
            try:
                # Validar datos
                if not self._validate_sensor_data(data):
                    emit('error', {'message': 'Datos de sensor inválidos'})
                    return
                
                # Broadcast a todas las salas
                emit('sensor_data_updated', {
                    'data': data,
                    'timestamp': datetime.utcnow().isoformat()
                }, broadcast=True)
                
                self._log("info", "Datos de sensor actualizados via WebSocket")
                
            except Exception as e:
                self._log("error", f"Error manejando datos de sensor: {e}")
                emit('error', {'message': 'Error procesando datos de sensor'})
        
        @self.socketio.on('alert_notification')
        def handle_alert_notification(data):
            """Manejar notificación de alerta"""
            try:
                # Validar datos de alerta
                if not self._validate_alert_data(data):
                    emit('error', {'message': 'Datos de alerta inválidos'})
                    return
                
                # Enviar a sala específica según el tipo de alerta
                target_room = data.get('target_room', 'public')
                
                emit('alert_received', {
                    'alert': data,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=target_room)
                
                self._log("info", f"Alerta enviada a sala {target_room}")
                
            except Exception as e:
                self._log("error", f"Error manejando alerta: {e}")
                emit('error', {'message': 'Error procesando alerta'})
    
    def _validate_sensor_data(self, data: Dict[str, Any]) -> bool:
        """Validar datos de sensor"""
        required_fields = ['nivel_agua', 'estado', 'timestamp']
        return all(field in data for field in required_fields)
    
    def _validate_alert_data(self, data: Dict[str, Any]) -> bool:
        """Validar datos de alerta"""
        required_fields = ['message', 'type', 'priority']
        return all(field in data for field in required_fields)
    
    def broadcast_sensor_data(self, sensor_data: Dict[str, Any]):
        """
        Broadcast datos de sensor a todos los clientes conectados
        
        Args:
            sensor_data: Datos del sensor
        """
        if self.socketio:
            self.socketio.emit('sensor_data_updated', {
                'data': sensor_data,
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)
            self._log("info", "Datos de sensor broadcast via WebSocket")
    
    def send_alert(self, alert_data: Dict[str, Any], target_room: str = 'public'):
        """
        Enviar alerta a una sala específica
        
        Args:
            alert_data: Datos de la alerta
            target_room: Sala objetivo (admin, operator, public)
        """
        if self.socketio:
            self.socketio.emit('alert_received', {
                'alert': alert_data,
                'timestamp': datetime.utcnow().isoformat()
            }, room=target_room)
            self._log("info", f"Alerta enviada a sala {target_room}")
    
    def send_system_notification(self, message: str, notification_type: str = 'info', target_room: str = 'public'):
        """
        Enviar notificación del sistema
        
        Args:
            message: Mensaje de notificación
            notification_type: Tipo de notificación (info, warning, error, success)
            target_room: Sala objetivo
        """
        if self.socketio:
            self.socketio.emit('system_notification', {
                'message': message,
                'type': notification_type,
                'timestamp': datetime.utcnow().isoformat()
            }, room=target_room)
            self._log("info", f"Notificación del sistema enviada a {target_room}")
    
    def get_connected_users_count(self) -> Dict[str, int]:
        """
        Obtener conteo de usuarios conectados por sala
        
        Returns:
            Dict[str, int]: Conteo por sala
        """
        return {
            room: len(users) 
            for room, users in self.room_users.items()
        }
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de conexión
        
        Returns:
            Dict[str, Any]: Estadísticas de conexión
        """
        return {
            'total_connections': len(self.connected_users),
            'users_by_room': self.get_connected_users_count(),
            'connected_users': list(self.connected_users.keys())
        }

# Instancia global del servicio WebSocket
websocket_service = WebSocketService()
