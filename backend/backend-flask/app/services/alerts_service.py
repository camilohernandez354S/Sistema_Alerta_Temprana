"""
Servicio de gestión de alertas para el Sistema de Alerta Temprana
Implementa la lógica de negocio para estados de alerta y control del buzzer
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pymongo import MongoClient
from bson import ObjectId
import requests
import os

# Configurar logger específico para alertas
alerts_logger = logging.getLogger('alerts_service')
alerts_logger.setLevel(logging.INFO)

class AlertsService:
    """Servicio para gestión de alertas del sistema"""
    
    def __init__(self):
        # Configuración de MongoDB
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('MONGO_DB', 'sistema_alerta')
        self.client = None
        self.db = None
        
        # Umbrales de alerta (configurables via env)
        self.umbral_inundacion = float(os.getenv('UMBRAL_INUNDACION', '15.0'))
        self.umbral_sequia = float(os.getenv('UMBRAL_SEQUIA', '40.0'))
        
        # URL del dispositivo IoT para control del buzzer
        self.iot_device_url = os.getenv('IOT_DEVICE_URL', 'http://localhost:8080')
        
        self._init_db()
    
    def _init_db(self):
        """Inicializar conexión a MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            alerts_logger.info("Conexión a MongoDB establecida correctamente")
        except Exception as e:
            alerts_logger.error(f"Error conectando a MongoDB: {e}")
            raise
    
    def _get_collection(self, collection_name: str):
        """Obtener colección de MongoDB"""
        return self.db[collection_name]
    
    def determinar_estado_alerta(self, nivel_agua: float) -> str:
        """
        Determinar el estado de alerta basado en el nivel de agua
        
        Args:
            nivel_agua: Nivel de agua en centímetros
            
        Returns:
            str: 'inundacion', 'sequia', 'normal'
        """
        if nivel_agua <= self.umbral_inundacion:
            return 'inundacion'
        elif nivel_agua >= self.umbral_sequia:
            return 'sequia'
        else:
            return 'normal'
    
    def procesar_nueva_medicion(self, distancia: float, user_id: str = 'system') -> Dict:
        """
        Procesar nueva medición y generar alerta si es necesario
        
        Args:
            distancia: Distancia medida por el sensor
            user_id: ID del usuario que procesó la medición
            
        Returns:
            dict: Información de la alerta procesada
        """
        try:
            estado_actual = self.determinar_estado_alerta(distancia)
            timestamp = datetime.utcnow()
            
            # Obtener última alerta activa
            alertas_collection = self._get_collection('alertas')
            ultima_alerta = alertas_collection.find_one(
                {'alerta_activa': True},
                sort=[('timestamp', -1)]
            )
            
            # Verificar si cambió el estado
            cambio_estado = False
            if not ultima_alerta or ultima_alerta.get('tipo_alerta') != estado_actual:
                cambio_estado = True
            
            # Si hay cambio de estado o nueva alerta crítica
            if cambio_estado and estado_actual != 'normal':
                # Desactivar alertas anteriores
                if ultima_alerta:
                    alertas_collection.update_one(
                        {'_id': ultima_alerta['_id']},
                        {
                            '$set': {
                                'alerta_activa': False,
                                'fecha_desactivacion': timestamp,
                                'desactivada_por': 'system_auto'
                            }
                        }
                    )
                
                # Crear nueva alerta
                nueva_alerta = {
                    'tipo_alerta': estado_actual,
                    'nivel_agua': distancia,
                    'alerta_activa': True,
                    'timestamp': timestamp,
                    'fecha_desactivacion': None,
                    'desactivada_por': None,
                    'buzzer_activo': True,
                    'creada_por': user_id,
                    'descripcion': self._generar_descripcion_alerta(estado_actual, distancia)
                }
                
                resultado = alertas_collection.insert_one(nueva_alerta)
                nueva_alerta['_id'] = str(resultado.inserted_id)
                
                # Activar buzzer en dispositivo IoT
                self._activar_buzzer_dispositivo(estado_actual)
                
                alerts_logger.info(
                    f"NUEVA_ALERTA - tipo={estado_actual}, nivel={distancia}cm, "
                    f"id={nueva_alerta['_id']}, user={user_id}"
                )
                
                return {
                    'alerta_generada': True,
                    'tipo_alerta': estado_actual,
                    'alerta_id': nueva_alerta['_id'],
                    'descripcion': nueva_alerta['descripcion']
                }
            
            # Si el estado es normal, desactivar alertas activas
            elif estado_actual == 'normal' and ultima_alerta and ultima_alerta.get('alerta_activa'):
                alertas_collection.update_one(
                    {'_id': ultima_alerta['_id']},
                    {
                        '$set': {
                            'alerta_activa': False,
                            'fecha_desactivacion': timestamp,
                            'desactivada_por': 'system_auto',
                            'buzzer_activo': False
                        }
                    }
                )
                
                # Desactivar buzzer
                self._desactivar_buzzer_dispositivo()
                
                alerts_logger.info(
                    f"ALERTA_DESACTIVADA_AUTO - id={ultima_alerta['_id']}, "
                    f"nivel={distancia}cm, user={user_id}"
                )
                
                return {
                    'alerta_generada': False,
                    'tipo_alerta': estado_actual,
                    'alerta_desactivada': str(ultima_alerta['_id'])
                }
            
            return {
                'alerta_generada': False,
                'tipo_alerta': estado_actual,
                'sin_cambios': True
            }
            
        except Exception as e:
            alerts_logger.error(f"Error procesando medición: {e}")
            raise
    
    def obtener_alertas_activas(self) -> List[Dict]:
        """
        Obtener todas las alertas activas
        
        Returns:
            list: Lista de alertas activas
        """
        try:
            alertas_collection = self._get_collection('alertas')
            alertas = list(alertas_collection.find(
                {'alerta_activa': True},
                sort=[('timestamp', -1)]
            ))
            
            # Convertir ObjectId a string
            for alerta in alertas:
                alerta['_id'] = str(alerta['_id'])
                alerta['timestamp'] = alerta['timestamp'].isoformat() + 'Z'
                if alerta.get('fecha_desactivacion'):
                    alerta['fecha_desactivacion'] = alerta['fecha_desactivacion'].isoformat() + 'Z'
            
            return alertas
            
        except Exception as e:
            alerts_logger.error(f"Error obteniendo alertas activas: {e}")
            raise
    
    def obtener_historial_alertas(self, limite: int = 50) -> List[Dict]:
        """
        Obtener historial de alertas (activas e inactivas)
        
        Args:
            limite: Número máximo de alertas a retornar
            
        Returns:
            list: Lista de alertas históricas
        """
        try:
            alertas_collection = self._get_collection('alertas')
            alertas = list(alertas_collection.find(
                {},
                sort=[('timestamp', -1)],
                limit=limite
            ))
            
            # Convertir ObjectId a string y fechas a ISO
            for alerta in alertas:
                alerta['_id'] = str(alerta['_id'])
                alerta['timestamp'] = alerta['timestamp'].isoformat() + 'Z'
                if alerta.get('fecha_desactivacion'):
                    alerta['fecha_desactivacion'] = alerta['fecha_desactivacion'].isoformat() + 'Z'
            
            return alertas
            
        except Exception as e:
            alerts_logger.error(f"Error obteniendo historial de alertas: {e}")
            raise
    
    def desactivar_alerta(self, alerta_id: str, user_id: str, motivo: str = 'manual') -> Dict:
        """
        Desactivar una alerta específica manualmente
        
        Args:
            alerta_id: ID de la alerta a desactivar
            user_id: ID del usuario que desactiva la alerta
            motivo: Motivo de la desactivación
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            alertas_collection = self._get_collection('alertas')
            
            # Verificar que la alerta existe y está activa
            alerta = alertas_collection.find_one({
                '_id': ObjectId(alerta_id),
                'alerta_activa': True
            })
            
            if not alerta:
                return {
                    'success': False,
                    'error': 'Alerta no encontrada o ya desactivada'
                }
            
            # Desactivar alerta
            resultado = alertas_collection.update_one(
                {'_id': ObjectId(alerta_id)},
                {
                    '$set': {
                        'alerta_activa': False,
                        'fecha_desactivacion': datetime.utcnow(),
                        'desactivada_por': user_id,
                        'motivo_desactivacion': motivo,
                        'buzzer_activo': False
                    }
                }
            )
            
            if resultado.modified_count > 0:
                # Desactivar buzzer en dispositivo IoT
                self._desactivar_buzzer_dispositivo()
                
                alerts_logger.info(
                    f"ALERTA_DESACTIVADA_MANUAL - id={alerta_id}, "
                    f"tipo={alerta['tipo_alerta']}, user={user_id}, motivo={motivo}"
                )
                
                return {
                    'success': True,
                    'alerta_id': alerta_id,
                    'tipo_alerta': alerta['tipo_alerta'],
                    'desactivada_por': user_id
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo desactivar la alerta'
                }
                
        except Exception as e:
            alerts_logger.error(f"Error desactivando alerta {alerta_id}: {e}")
            raise
    
    def obtener_estado_sistema(self) -> Dict:
        """
        Obtener el estado actual del sistema de alertas
        
        Returns:
            dict: Estado actual del sistema
        """
        try:
            # Obtener última medición
            mediciones_collection = self._get_collection('mediciones')
            ultima_medicion = mediciones_collection.find_one(
                {},
                sort=[('fecha', -1)]
            )
            
            # Obtener alertas activas
            alertas_activas = self.obtener_alertas_activas()
            
            if ultima_medicion:
                nivel_actual = ultima_medicion.get('distancia', 0)
                estado_actual = self.determinar_estado_alerta(nivel_actual)
            else:
                nivel_actual = 0
                estado_actual = 'normal'
            
            return {
                'nivel_actual': nivel_actual,
                'estado_actual': estado_actual,
                'alertas_activas': len(alertas_activas),
                'buzzer_activo': any(a.get('buzzer_activo', False) for a in alertas_activas),
                'ultima_actualizacion': datetime.utcnow().isoformat() + 'Z',
                'umbrales': {
                    'inundacion': self.umbral_inundacion,
                    'sequia': self.umbral_sequia
                }
            }
            
        except Exception as e:
            alerts_logger.error(f"Error obteniendo estado del sistema: {e}")
            raise
    
    def _generar_descripcion_alerta(self, tipo_alerta: str, nivel: float) -> str:
        """Generar descripción legible para la alerta"""
        descripciones = {
            'inundacion': f'🌊 ALERTA DE INUNDACIÓN: Nivel de agua crítico ({nivel:.1f} cm). '
                         f'Por debajo del umbral de {self.umbral_inundacion} cm.',
            'sequia': f'🏜️ ALERTA DE SEQUÍA: Nivel de agua bajo ({nivel:.1f} cm). '
                     f'Por encima del umbral de {self.umbral_sequia} cm.',
            'normal': f'✅ Nivel normal: {nivel:.1f} cm dentro del rango aceptable.'
        }
        return descripciones.get(tipo_alerta, f'Estado: {tipo_alerta}, Nivel: {nivel:.1f} cm')
    
    def _activar_buzzer_dispositivo(self, tipo_alerta: str):
        """Enviar comando para activar buzzer en dispositivo IoT"""
        try:
            # Importar el servicio de control de dispositivos
            from app.services.device_control_service import device_control_service
            
            # Configurar frecuencia según tipo de alerta
            frecuencias = {
                'inundacion': 1500,  # Tono agudo para inundación
                'sequia': 400        # Tono grave para sequía
            }
            
            frecuencia = frecuencias.get(tipo_alerta, 1000)
            
            # Activar buzzer usando el servicio de control
            resultado = device_control_service.activate_buzzer(
                alert_type=tipo_alerta,
                frequency=frecuencia
            )
            
            if resultado.get('status') == 'success':
                alerts_logger.info(f"BUZZER_ACTIVADO - tipo={tipo_alerta}, frecuencia={frecuencia}Hz")
            else:
                alerts_logger.warning(f"Error activando buzzer: {resultado.get('message', 'Unknown error')}")
            
        except Exception as e:
            alerts_logger.warning(f"Error activando buzzer: {e}")
    
    def _desactivar_buzzer_dispositivo(self):
        """Enviar comando para desactivar buzzer en dispositivo IoT"""
        try:
            # Importar el servicio de control de dispositivos
            from app.services.device_control_service import device_control_service
            
            # Desactivar buzzer usando el servicio de control
            resultado = device_control_service.deactivate_buzzer()
            
            if resultado.get('status') == 'success':
                alerts_logger.info("BUZZER_DESACTIVADO")
            else:
                alerts_logger.warning(f"Error desactivando buzzer: {resultado.get('message', 'Unknown error')}")
            
        except Exception as e:
            alerts_logger.warning(f"Error desactivando buzzer: {e}")
    
    def cleanup(self):
        """Limpiar recursos al cerrar el servicio"""
        if self.client:
            self.client.close()
            alerts_logger.info("Conexión MongoDB cerrada")

# Instancia global del servicio
alerts_service = AlertsService()
