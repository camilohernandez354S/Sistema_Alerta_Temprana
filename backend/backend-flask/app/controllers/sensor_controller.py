"""
Controlador para operaciones de sensores
"""
from flask import request, jsonify, current_app
from http import HTTPStatus
from typing import Tuple
from datetime import datetime

from app.models.sensor_model import (
    EstadoSensorStats, 
    LecturaArduinoRequest, 
    LecturaArduinoResponse,
    LecturaArduinoDocument,
    ConsultaLecturasRequest
)
from app.services.sensor_service import SensorService

class SensorController:
    """Controlador para manejar requests de sensores"""
    
    def __init__(self, sensor_service: SensorService):
        """
        Inicializar controlador
        
        Args:
            sensor_service: Servicio de sensores
        """
        self.sensor_service = sensor_service
        current_app.logger.info("SensorController inicializado")

    def proceso_leer_sensor(self) -> Tuple[dict, int]:
        """
        Procesar una nueva lectura del sensor
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            data = request.json
            if not data or 'nivel_agua' not in data:
                current_app.logger.warning("Request sin campo nivel_agua")
                return {"error": "Se requiere el campo nivel_agua"}, HTTPStatus.BAD_REQUEST
                
            # Validar tipo de dato
            try:
                nivel_agua = float(data['nivel_agua'])
            except (ValueError, TypeError):
                return {"error": "nivel_agua debe ser un número"}, HTTPStatus.BAD_REQUEST
                
            # Procesar la lectura
            documento = self.sensor_service.proceso_leer_sensor(nivel_agua)
            
            if documento:
                return {
                    "mensaje": "Lectura procesada exitosamente",
                    "data": documento.dict()
                }, HTTPStatus.OK
            else:
                return {"error": "Error procesando la lectura"}, HTTPStatus.INTERNAL_SERVER_ERROR
                
        except ValueError as ve:
            current_app.logger.warning(f"Error de validación: {ve}")
            return {"error": str(ve)}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            current_app.logger.error(f"Error inesperado: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR

    def proceso_lecturas(self) -> Tuple[dict, int]:
        """
        Procesar múltiples lecturas del sensor
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            data = request.json
            if not data or not isinstance(data, list):
                return {"error": "Se requiere una lista de lecturas"}, HTTPStatus.BAD_REQUEST
                
            # Validar formato de cada lectura
            for i, lectura in enumerate(data):
                if not isinstance(lectura, dict) or 'raw_data' not in lectura:
                    return {
                        "error": f"Lectura {i+1}: debe ser un objeto con clave 'raw_data'"
                    }, HTTPStatus.BAD_REQUEST
                    
            # Procesar las lecturas
            documentos = self.sensor_service.proceso_lecturas(data)
            
            return {
                "mensaje": f"Procesadas {len(documentos)} de {len(data)} lecturas",
                "data": [doc.dict() for doc in documentos],
                "procesadas": len(documentos),
                "total": len(data)
            }, HTTPStatus.OK
            
        except ValueError as ve:
            current_app.logger.warning(f"Error de validación: {ve}")
            return {"error": str(ve)}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            current_app.logger.error(f"Error procesando lecturas: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    def get_predicciones(self) -> Tuple[dict, int]:
        """
        Generar predicciones de nivel de agua con múltiples horizontes
        
        Query Parameters:
            horizons: Lista de horizontes en minutos (ej: 30,60,180)
            
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            # Obtener parámetros de query
            horizons_param = request.args.get('horizons', '30,60,180')
            
            try:
                horizons = [int(h.strip()) for h in horizons_param.split(',')]
                # Validar horizontes
                if any(h <= 0 for h in horizons):
                    return {
                        "error": "Los horizontes deben ser números positivos"
                    }, HTTPStatus.BAD_REQUEST
                if len(horizons) > 10:
                    return {
                        "error": "Máximo 10 horizontes permitidos"
                    }, HTTPStatus.BAD_REQUEST
            except ValueError:
                return {
                    "error": "Formato de horizontes inválido. Use: 30,60,180"
                }, HTTPStatus.BAD_REQUEST
            
            # Obtener datos históricos (últimas 24 horas o 500 registros)
            datos = self.sensor_service.obtener_datos_historicos(dias=1)
            if len(datos) < 500:  # Si no hay 500 en 1 día, obtener más
                datos = self.sensor_service.get_ultimas_lecturas(limit=500)
            
            if not datos:
                return {
                    "error": {
                        "message": "No hay suficientes datos históricos para hacer predicciones",
                        "code": "INSUFFICIENT_DATA"
                    }
                }, HTTPStatus.NOT_FOUND
                
            # Generar predicciones usando el nuevo servicio robusto
            resultado = self.sensor_service.prediction_service.generar_predicciones_multi_horizonte(
                datos, horizons
            )
            
            # Verificar si hay error en el resultado
            if "error" in resultado:
                return resultado, HTTPStatus.INTERNAL_SERVER_ERROR
            
            return resultado, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error generando predicciones: {e}")
            return {
                "error": {
                    "message": f"Error interno generando predicciones: {str(e)}",
                    "code": "PREDICTION_FAILED"
                }
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_todas_lecturas(self) -> Tuple[dict, int]:
        """
        Obtener lecturas del sensor con parámetros de filtrado
        
        Query Parameters:
            limit: Número máximo de lecturas (default: 500, max: 1000)
            since: Timestamp ISO desde cuando obtener lecturas (opcional)
            order: Orden de resultados ('asc' o 'desc', default: 'desc')
            
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            # Obtener parámetros de query
            limit = request.args.get('limit', 500, type=int)
            since_param = request.args.get('since')
            order = request.args.get('order', 'desc')
            
            # Validar parámetros
            if limit <= 0 or limit > 1000:
                return {
                    "error": "El parámetro 'limit' debe estar entre 1 y 1000"
                }, HTTPStatus.BAD_REQUEST
            
            if order not in ['asc', 'desc']:
                return {
                    "error": "El parámetro 'order' debe ser 'asc' o 'desc'"
                }, HTTPStatus.BAD_REQUEST
            
            # Obtener lecturas según parámetros
            if since_param:
                try:
                    # Parsear timestamp ISO
                    since_dt = datetime.fromisoformat(since_param.replace('Z', '+00:00'))
                    documentos = self.sensor_service.get_lecturas_desde(since_dt, limit)
                except ValueError:
                    return {
                        "error": "Formato de timestamp 'since' inválido. Use formato ISO 8601"
                    }, HTTPStatus.BAD_REQUEST
            else:
                documentos = self.sensor_service.get_ultimas_lecturas(limit)
            
            # Formatear respuesta consistente
            resultado = []
            for doc in documentos:
                resultado.append({
                    "id": str(doc.id),
                    "nivel_cm": float(doc.nivel_agua),
                    "estado": doc.estado,
                    "timestamp": doc.timestamp
                })
            
            # Ordenar según parámetro
            if order == 'asc':
                resultado.sort(key=lambda x: x['timestamp'])
            else:
                resultado.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return {
                "lecturas": resultado,
                "total": len(resultado),
                "limit": limit,
                "order": order
            }, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo lecturas: {e}")
            return {
                "error": "Error interno del servidor"
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_ultima_lectura(self) -> Tuple[dict, int]:
        """
        Obtener la última lectura del sensor
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            documento = self.sensor_service.get_ultima_lectura()
            
            if documento:
                resultado = {
                    "_id": str(documento.id),
                    "nivel_agua": documento.nivel_agua,
                    "estado": documento.estado,
                    "timestamp": documento.timestamp
                }
                return resultado, HTTPStatus.OK
            else:
                return {"error": "No hay lecturas disponibles"}, HTTPStatus.NOT_FOUND
                
        except Exception as e:
            current_app.logger.error(f"Error obteniendo última lectura: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_lecturas_rango(self, rango: str) -> Tuple[dict, int]:
        """
        Obtener lecturas en un rango de tiempo
        
        Args:
            rango: Rango de tiempo ('1h', '24h', '7d')
            
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            # Validar rango
            rangos_validos = ['1h', '24h', '7d']
            if rango not in rangos_validos:
                return {
                    "error": f"Rango inválido. Debe ser uno de: {', '.join(rangos_validos)}"
                }, HTTPStatus.BAD_REQUEST
            
            documentos = self.sensor_service.get_lecturas_rango(rango)
            
            resultado = []
            for doc in documentos:
                resultado.append({
                    "_id": str(doc.id),
                    "nivel_agua": float(doc.nivel_agua),
                    "estado": doc.estado,
                    "timestamp": doc.timestamp
                })
            
            return {
                "lecturas": resultado,
                "rango": rango,
                "total": len(resultado)
            }, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo lecturas por rango: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_estadisticas_diarias(self) -> Tuple[dict, int]:
        """
        Obtener estadísticas diarias del nivel de agua
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            estadisticas = self.sensor_service.obtener_estadisticas_diarias()
            return estadisticas, HTTPStatus.OK
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas diarias: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR
        
    def obtener_estadisticas_estados(self) -> Tuple[dict, int]:
        """
        Obtener estadísticas de estados del sensor
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            return self.sensor_service.obtener_estadisticas_estados()
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas de estados: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_alertas(self) -> Tuple[dict, int]:
        """
        Obtener alertas recientes (lecturas en estado de sequía o inundación)
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            limit = request.args.get('limit', 10, type=int)
            if limit <= 0 or limit > 100:
                return {"error": "El límite debe estar entre 1 y 100"}, HTTPStatus.BAD_REQUEST
                
            alertas = self.sensor_service.get_alertas(limit)
            
            return {
                "alertas": alertas,
                "total": len(alertas)
            }, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo alertas: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_estado_sistema(self) -> Tuple[dict, int]:
        """
        Obtener estado general del sistema
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            estado = self.sensor_service.get_estado_sistema()
            return estado, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estado del sistema: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    def verify_blockchain(self) -> Tuple[dict, int]:
        """
        Verificar integridad de la blockchain
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            if self.sensor_service.blockchain.validate_chain():
                return {
                    "valid": True, 
                    "message": "La cadena de bloques es válida"
                }, HTTPStatus.OK
            else:
                return {
                    "valid": False, 
                    "message": "La cadena de bloques ha sido comprometida"
                }, HTTPStatus.BAD_REQUEST
        except Exception as e:
            current_app.logger.error(f"Error verificando blockchain: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    def health_check(self) -> Tuple[dict, int]:
        """
        Health check del servicio
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            db_healthy = self.sensor_service.health_check()
            blockchain_healthy = self.sensor_service.blockchain.validate_chain()
            
            status = "healthy" if db_healthy and blockchain_healthy else "degraded"
            
            return {
                "status": status,
                "checks": {
                    "database": "ok" if db_healthy else "error",
                    "blockchain": "ok" if blockchain_healthy else "error"
                },
                "timestamp": request.environ.get('REQUEST_TIME', 'unknown')
            }, HTTPStatus.OK if status == "healthy" else HTTPStatus.SERVICE_UNAVAILABLE
            
        except Exception as e:
            current_app.logger.error(f"Error en health check: {e}")
            return {
                "status": "error",
                "error": "Error interno del servidor"
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    def insertar_datos_prueba(self) -> Tuple[dict, int]:
        """
        Insertar datos de prueba en la base de datos
        Solo para desarrollo
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            from datetime import datetime, timedelta
            import random
            
            # Generar datos de prueba para las últimas 24 horas
            datos_insertados = 0
            ahora = datetime.now()
            
            for i in range(24):  # 24 puntos de datos (1 por hora)
                timestamp = ahora - timedelta(hours=i)
                
                # Generar nivel de agua aleatorio pero realista
                base_level = 30.0  # Nivel base
                variation = random.uniform(-10, 15)  # Variación
                nivel_agua = max(5.0, min(100.0, base_level + variation))  # Entre 5 y 100 cm
                
                # Procesar la lectura usando el servicio existente
                documento = self.sensor_service.proceso_leer_sensor(nivel_agua)
                
                if documento:
                    # Actualizar el timestamp para que sea histórico
                    try:
                        from bson import ObjectId
                        self.sensor_service.repository.collection.update_one(
                            {"_id": ObjectId(documento.id)},
                            {"$set": {"timestamp": timestamp.isoformat()}}
                        )
                        datos_insertados += 1
                    except Exception as e:
                        current_app.logger.warning(f"Error actualizando timestamp: {e}")
            
            current_app.logger.info(f"Insertados {datos_insertados} registros de prueba")
            
            return {
                "mensaje": "Datos de prueba insertados correctamente",
                "total": datos_insertados,
                "periodo": "últimas 24 horas"
            }, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error insertando datos de prueba: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR

    # =============================================================================
    # NUEVOS MÉTODOS PARA DATOS ESTRUCTURADOS DEL ARDUINO
    # =============================================================================

    def procesar_lectura_arduino(self, lectura_data: LecturaArduinoRequest) -> Tuple[dict, int]:
        """
        Procesar una nueva lectura estructurada del Arduino
        
        Args:
            lectura_data: Datos validados de la lectura del Arduino
            
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            current_app.logger.info(f"Procesando lectura Arduino: nivel={lectura_data.nivel_cm}cm, estado={lectura_data.estado}")
            
            # Validar datos críticos
            if lectura_data.nivel_cm < 0:
                current_app.logger.warning(f"Nivel de agua negativo rechazado: {lectura_data.nivel_cm}")
                return {
                    "error": "Nivel de agua no puede ser negativo",
                    "code": "INVALID_LEVEL"
                }, HTTPStatus.BAD_REQUEST
            
            if lectura_data.estado not in ['Inundación', 'Normal', 'Sequía', 'Error']:
                current_app.logger.warning(f"Estado inválido rechazado: {lectura_data.estado}")
                return {
                    "error": f"Estado inválido: {lectura_data.estado}",
                    "code": "INVALID_STATE"
                }, HTTPStatus.BAD_REQUEST
            
            # Guardar en MongoDB usando el servicio
            documento_guardado = self.sensor_service.guardar_lectura_arduino(lectura_data)
            
            if documento_guardado:
                # Crear respuesta estructurada
                respuesta_data = LecturaArduinoDocument(
                    id=str(documento_guardado['_id']),
                    nivel_cm=documento_guardado['nivel_cm'],
                    estado=documento_guardado['estado'],
                    intervalo_ms=documento_guardado['intervalo_ms'],
                    velocidad_cm_por_s=documento_guardado.get('velocidad_cm_por_s'),
                    timestamp=documento_guardado['timestamp']
                )
                
                return {
                    "mensaje": "Lectura procesada exitosamente",
                    "data": respuesta_data.dict(by_alias=True)
                }, HTTPStatus.OK
            else:
                return {
                    "error": "Error guardando lectura en base de datos",
                    "code": "DATABASE_ERROR"
                }, HTTPStatus.INTERNAL_SERVER_ERROR
                
        except Exception as e:
            current_app.logger.error(f"Error procesando lectura Arduino: {e}")
            return {
                "error": "Error interno del servidor",
                "code": "INTERNAL_ERROR"
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    def consultar_lecturas_arduino(self, consulta_params: ConsultaLecturasRequest) -> Tuple[dict, int]:
        """
        Consultar lecturas del Arduino con filtros opcionales
        
        Args:
            consulta_params: Parámetros de consulta validados
            
        Returns:
            Tuple[dict, int]: Lista de lecturas y código de estado
        """
        try:
            current_app.logger.info(f"Consultando lecturas Arduino: limit={consulta_params.limit}, since={consulta_params.since}")
            
            # Obtener lecturas del servicio
            lecturas = self.sensor_service.consultar_lecturas_arduino(
                limit=consulta_params.limit,
                since=consulta_params.since
            )
            
            # Convertir a formato de respuesta
            lecturas_respuesta = []
            for lectura in lecturas:
                lecturas_respuesta.append({
                    "nivel_cm": lectura['nivel_cm'],
                    "estado": lectura['estado'],
                    "intervalo_ms": lectura['intervalo_ms'],
                    "velocidad_cm_por_s": lectura.get('velocidad_cm_por_s'),
                    "timestamp": lectura['timestamp']
                })
            
            return lecturas_respuesta, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error consultando lecturas Arduino: {e}")
            return {
                "error": "Error interno del servidor",
                "code": "INTERNAL_ERROR"
            }, HTTPStatus.INTERNAL_SERVER_ERROR