"""
Servicio para operaciones geoespaciales del Sistema de Alerta Temprana
Maneja consultas geográficas, índices 2dsphere y operaciones de proximidad
"""
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import logging

class GeospatialService:
    """
    Servicio especializado en operaciones geoespaciales
    Principio SRP: Responsabilidad única de manejar datos geográficos
    """
    
    def __init__(self):
        """Inicializar conexión a MongoDB usando variables de entorno"""
        import os
        from flask import current_app
        
        # Obtener configuración de MongoDB desde variables de entorno o configuración de Flask
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGO_DB', 'sistema_alerta')
        
        # Intentar obtener configuración de Flask si está disponible
        try:
            if current_app:
                mongo_uri = current_app.config.get('MONGO_URI', mongo_uri)
                db_name = current_app.config.get('MONGO_DB', db_name)
        except:
            pass  # Si no hay contexto de Flask, usar configuración de variables de entorno
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.mediciones_collection = self.db['mediciones']
        self.sensores_collection = self.db['sensores']
        
        # Configurar logger
        self.logger = logging.getLogger(__name__)
        
        # Crear índices geoespaciales al inicializar
        self._create_geospatial_indexes()
    
    def _create_geospatial_indexes(self):
        """
        Crear índices 2dsphere para optimizar consultas geoespaciales
        Se ejecuta automáticamente al inicializar el servicio
        """
        try:
            # Índice 2dsphere en la colección mediciones
            self.mediciones_collection.create_index([("location", "2dsphere")])
            self.logger.info("✅ Índice 2dsphere creado en colección 'mediciones'")
            
            # Índice 2dsphere en la colección sensores
            self.sensores_collection.create_index([("location", "2dsphere")])
            self.logger.info("✅ Índice 2dsphere creado en colección 'sensores'")
            
        except Exception as e:
            self.logger.error(f"❌ Error creando índices geoespaciales: {e}")
    
    def create_sensor_with_location(self, sensor_id, lat, lng, nombre=None, descripcion=None):
        """
        Crear o actualizar un sensor con coordenadas geográficas
        
        Args:
            sensor_id (str): ID único del sensor
            lat (float): Latitud
            lng (float): Longitud
            nombre (str): Nombre descriptivo del sensor
            descripcion (str): Descripción del sensor
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar coordenadas
            if not (-90 <= lat <= 90):
                raise ValueError("Latitud debe estar entre -90 y 90")
            if not (-180 <= lng <= 180):
                raise ValueError("Longitud debe estar entre -180 y 180")
            
            # Crear documento del sensor con datos geoespaciales
            sensor_doc = {
                'sensor_id': sensor_id,
                'location': {
                    'type': 'Point',
                    'coordinates': [lng, lat]  # MongoDB usa [longitud, latitud]
                },
                'nombre': nombre or f"Sensor {sensor_id}",
                'descripcion': descripcion or f"Sensor de nivel de agua en {lat}, {lng}",
                'activo': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Upsert: actualizar si existe, crear si no existe
            result = self.sensores_collection.update_one(
                {'sensor_id': sensor_id},
                {'$set': sensor_doc},
                upsert=True
            )
            
            self.logger.info(f"✅ Sensor {sensor_id} configurado en {lat}, {lng}")
            
            return {
                'success': True,
                'sensor_id': sensor_id,
                'location': {'lat': lat, 'lng': lng},
                'operation': 'created' if result.upserted_id else 'updated'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error creando sensor {sensor_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_measurement_with_location(self, sensor_id, nivel, estado, lat=None, lng=None):
        """
        Guardar medición con datos geoespaciales
        
        Args:
            sensor_id (str): ID del sensor
            nivel (float): Nivel de agua en cm
            estado (str): Estado (sequia, normal, inundacion)
            lat (float): Latitud (opcional, se obtiene del sensor si no se proporciona)
            lng (float): Longitud (opcional, se obtiene del sensor si no se proporciona)
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Si no se proporcionan coordenadas, obtenerlas del sensor
            if lat is None or lng is None:
                sensor = self.sensores_collection.find_one({'sensor_id': sensor_id})
                if not sensor or 'location' not in sensor:
                    raise ValueError(f"Sensor {sensor_id} no encontrado o sin coordenadas")
                
                coords = sensor['location']['coordinates']
                lng, lat = coords[0], coords[1]
            
            # Crear documento de medición con datos geoespaciales
            medicion_doc = {
                'sensor_id': sensor_id,
                'location': {
                    'type': 'Point',
                    'coordinates': [lng, lat]
                },
                'nivel': float(nivel),
                'estado': estado,
                'timestamp': datetime.utcnow()
            }
            
            # Insertar medición
            result = self.mediciones_collection.insert_one(medicion_doc)
            
            self.logger.info(f"✅ Medición guardada: {nivel}cm en {lat}, {lng}")
            
            return {
                'success': True,
                'medicion_id': str(result.inserted_id),
                'sensor_id': sensor_id,
                'location': {'lat': lat, 'lng': lng},
                'nivel': nivel,
                'estado': estado
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando medición: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_alerts_in_radius(self, lat, lng, radius_meters=5000):
        """
        Obtener alertas dentro de un radio circular específico
        
        Args:
            lat (float): Latitud del punto central
            lng (float): Longitud del punto central
            radius_meters (int): Radio en metros (default: 5000m)
            
        Returns:
            list: Lista de alertas dentro del radio
        """
        try:
            # Validar coordenadas
            if not (-90 <= lat <= 90):
                raise ValueError("Latitud debe estar entre -90 y 90")
            if not (-180 <= lng <= 180):
                raise ValueError("Longitud debe estar entre -180 y 180")
            
            # Consulta geoespacial usando $near con $maxDistance
            # $maxDistance está en metros para consultas 2dsphere
            query = {
                'location': {
                    '$near': {
                        '$geometry': {
                            'type': 'Point',
                            'coordinates': [lng, lat]
                        },
                        '$maxDistance': radius_meters
                    }
                },
                'estado': {'$in': ['sequia', 'inundacion']}  # Solo alertas, no estado normal
            }
            
            # Ejecutar consulta
            alerts = list(self.mediciones_collection.find(query).sort('timestamp', -1).limit(100))
            
            # Procesar resultados
            processed_alerts = []
            for alert in alerts:
                # Convertir ObjectId a string
                alert['_id'] = str(alert['_id'])
                
                # Convertir timestamp a ISO string
                if isinstance(alert['timestamp'], datetime):
                    alert['timestamp'] = alert['timestamp'].isoformat() + 'Z'
                
                # Agregar información del sensor si está disponible
                sensor_info = self.sensores_collection.find_one({'sensor_id': alert['sensor_id']})
                if sensor_info:
                    alert['sensor_nombre'] = sensor_info.get('nombre', alert['sensor_id'])
                    alert['sensor_descripcion'] = sensor_info.get('descripcion', '')
                
                # Calcular distancia aproximada (opcional)
                coords = alert['location']['coordinates']
                alert['distancia_km'] = self._calculate_distance(lat, lng, coords[1], coords[0])
                
                processed_alerts.append(alert)
            
            self.logger.info(f"✅ Encontradas {len(processed_alerts)} alertas en radio de {radius_meters}m")
            
            return {
                'success': True,
                'alerts': processed_alerts,
                'total': len(processed_alerts),
                'center': {'lat': lat, 'lng': lng},
                'radius_meters': radius_meters,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo alertas en radio: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': []
            }
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """
        Calcular distancia aproximada entre dos puntos usando fórmula de Haversine
        """
        import math
        
        # Radio de la Tierra en kilómetros
        R = 6371.0
        
        # Convertir a radianes
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        # Diferencia de coordenadas
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        # Fórmula de Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return round(R * c, 2)
    
    def get_all_sensors(self):
        """
        Obtener todos los sensores registrados con sus ubicaciones
        
        Returns:
            list: Lista de sensores con ubicaciones
        """
        try:
            sensors = list(self.sensores_collection.find({'activo': True}))
            
            processed_sensors = []
            for sensor in sensors:
                sensor['_id'] = str(sensor['_id'])
                if 'created_at' in sensor and isinstance(sensor['created_at'], datetime):
                    sensor['created_at'] = sensor['created_at'].isoformat() + 'Z'
                if 'updated_at' in sensor and isinstance(sensor['updated_at'], datetime):
                    sensor['updated_at'] = sensor['updated_at'].isoformat() + 'Z'
                
                processed_sensors.append(sensor)
            
            return {
                'success': True,
                'sensors': processed_sensors,
                'total': len(processed_sensors)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo sensores: {e}")
            return {
                'success': False,
                'error': str(e),
                'sensors': []
            }
    
    def close_connection(self):
        """Cerrar conexión a MongoDB"""
        if self.client:
            self.client.close()

# Instancia global del servicio
geospatial_service = GeospatialService()
