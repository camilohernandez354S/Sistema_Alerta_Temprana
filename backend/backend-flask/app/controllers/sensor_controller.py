"""
Controlador para operaciones de sensores
"""
from flask import request, jsonify, current_app
from http import HTTPStatus
from typing import Tuple

from app.models.sensor_model import EstadoSensorStats
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
        Generar predicciones de nivel de agua
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            # Obtener datos históricos
            datos = self.sensor_service.obtener_datos_historicos()
            
            if not datos:
                return {
                    "error": "No hay suficientes datos históricos para hacer predicciones"
                }, HTTPStatus.NOT_FOUND
                
            # Generar predicciones
            predicciones = self.sensor_service.generar_predicciones(datos)
            
            return {
                "predicciones": predicciones,
                "datos_utilizados": len(datos)
            }, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error generando predicciones: {e}")
            return {"error": "Error al generar predicciones"}, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_todas_lecturas(self) -> Tuple[dict, int]:
        """
        Obtener todas las lecturas del sensor
        
        Returns:
            Tuple[dict, int]: Respuesta y código de estado
        """
        try:
            documentos = self.sensor_service.get_todas_lecturas()
            
            resultado = []
            for doc in documentos:
                resultado.append({
                    "_id": str(doc.id),
                    "nivel_agua": doc.nivel_agua,
                    "estado": doc.estado,
                    "timestamp": doc.timestamp
                })
            
            return {
                "lecturas": resultado,
                "total": len(resultado)
            }, HTTPStatus.OK
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo lecturas: {e}")
            return {"error": "Error interno del servidor"}, HTTPStatus.INTERNAL_SERVER_ERROR

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
