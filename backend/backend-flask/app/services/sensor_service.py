"""
Servicio de negocio para sensores
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from flask import current_app
from http import HTTPStatus

from app.models.sensor_model import (
    SensorReading, SensorData, SensorDocumentGuardado, 
    SensorDocumentObtenido, SensorDocumentRangoTiempo, EstadoSensorStats,
    LecturaArduinoRequest, LecturaArduinoDocument
)
from app.models.blockchain_model import Blockchain
from app.repositories.sensor_repository import SensorRepository
from app.services.prediction_service import PredictionService

class SensorService:
    """Servicio para lógica de negocio de sensores"""
    
    def __init__(self, repository: SensorRepository):
        """
        Inicializar servicio
        
        Args:
            repository: Repository para acceso a datos
        """
        self.repository = repository
        self.blockchain = Blockchain()
        self.prediction_service = PredictionService()
        
        current_app.logger.info("SensorService inicializado")
    
    def proceso_leer_sensor(self, nivel_agua: float) -> Optional[SensorDocumentGuardado]:
        """
        Procesar una nueva lectura del sensor
        
        Args:
            nivel_agua: Nivel de agua en centímetros
            
        Returns:
            Optional[SensorDocumentGuardado]: Documento procesado o None
        """
        try:
            # Crear datos procesados
            data = SensorData(
                nivel_agua=nivel_agua,
                estado=self._determinar_estado(nivel_agua),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Verificar integridad de blockchain
            if not self.blockchain.validate_chain():
                raise ValueError("La cadena de bloques ha sido comprometida")
            
            # Crear documento para guardar
            doc = SensorDocumentGuardado.parse_obj(data.dict())
            
            # Guardar en base de datos
            doc_id = self.repository.insert_one(doc)
            if not doc_id:
                raise Exception("Error guardando en base de datos")
            
            # Agregar a blockchain
            self.blockchain.add_block(data.dict())
            
            # Verificar integridad después de agregar
            if not self.blockchain.validate_chain():
                raise ValueError("Error al agregar el nuevo bloque a la cadena")
            
            current_app.logger.info(f"Lectura procesada exitosamente: {nivel_agua}cm")
            return doc
            
        except ValueError as ve:
            current_app.logger.warning(f"Error de validación: {ve}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error procesando lectura: {e}")
            return None
    
    def proceso_lecturas(self, lecturas: List[Dict]) -> List[SensorDocumentGuardado]:
        """
        Procesar múltiples lecturas
        
        Args:
            lecturas: Lista de lecturas
            
        Returns:
            List[SensorDocumentGuardado]: Lista de documentos procesados
        """
        documentos = []
        for lectura in lecturas:
            try:
                # Extraer nivel de agua del formato raw_data
                reading = SensorReading(nivel_agua=lectura['raw_data'])
                nivel_agua = reading.extraer_nivel_agua()
                
                doc = self.proceso_leer_sensor(nivel_agua)
                if doc:
                    documentos.append(doc)
            except Exception as e:
                current_app.logger.warning(f"Error procesando lectura individual: {e}")
                continue
        
        current_app.logger.info(f"Procesadas {len(documentos)} de {len(lecturas)} lecturas")
        return documentos
    
    def get_todas_lecturas(self) -> List[SensorDocumentObtenido]:
        """Obtener todas las lecturas"""
        return self.repository.find_all()
    
    def get_ultima_lectura(self) -> Optional[SensorDocumentObtenido]:
        """Obtener la última lectura"""
        return self.repository.find_latest()
    
    def get_ultimas_lecturas(self, limit: int = 5) -> List[SensorDocumentObtenido]:
        """Obtener las últimas N lecturas"""
        return self.repository.find_all(limit=limit)
    
    def get_lecturas_desde(self, desde: datetime, limit: int = 500) -> List[SensorDocumentObtenido]:
        """
        Obtener lecturas desde una fecha específica
        
        Args:
            desde: Fecha desde cuando obtener lecturas
            limit: Número máximo de lecturas
            
        Returns:
            List[SensorDocumentObtenido]: Lista de lecturas
        """
        try:
            desde_str = desde.strftime('%Y-%m-%d %H:%M:%S')
            return self.repository.find_by_time_range(desde_str, limit=limit)
        except Exception as e:
            current_app.logger.error(f"Error obteniendo lecturas desde fecha: {e}")
            return []
    
    def get_lecturas_rango(self, rango: str) -> List[SensorDocumentRangoTiempo]:
        """
        Obtener lecturas en un rango de tiempo
        
        Args:
            rango: Rango de tiempo ('1h', '24h', '7d')
            
        Returns:
            List[SensorDocumentRangoTiempo]: Lista de lecturas
        """
        try:
            now = datetime.now()
            
            # Determinar fecha de inicio
            if rango == '1h':
                start_time = now - timedelta(hours=1)
            elif rango == '24h':
                start_time = now - timedelta(hours=24)
            elif rango == '7d':
                start_time = now - timedelta(days=7)
            else:
                current_app.logger.warning(f"Rango inválido: {rango}")
                return []
            
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            return self.repository.find_by_time_range(start_time_str)
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo lecturas en rango: {e}")
            return []
    
    def obtener_datos_historicos(self, dias: int = 30) -> List[SensorDocumentObtenido]:
        """
        Obtener datos históricos
        
        Args:
            dias: Número de días hacia atrás
            
        Returns:
            List[SensorDocumentObtenido]: Lista de documentos históricos
        """
        try:
            fecha_inicio = datetime.now() - timedelta(days=dias)
            fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d %H:%M:%S")
            
            return self.repository.find_by_time_range(fecha_inicio_str)
        except Exception as e:
            current_app.logger.error(f"Error obteniendo datos históricos: {e}")
            return []
    
    def generar_predicciones(self, datos: List[SensorDocumentObtenido]) -> List[Dict[str, Any]]:
        """
        Generar predicciones usando servicio especializado
        
        Args:
            datos: Datos históricos
            
        Returns:
            List[Dict[str, Any]]: Lista de predicciones
        """
        return self.prediction_service.generar_predicciones(datos)
    
    def obtener_estadisticas_estados(self) -> Tuple[EstadoSensorStats, HTTPStatus]:
        """
        Obtener estadísticas de estados
        
        Returns:
            Tuple[EstadoSensorStats, HTTPStatus]: Estadísticas y código de estado
        """
        try:
            stats_dict = self.repository.count_by_estado()
            stats = EstadoSensorStats(**stats_dict)
            return stats, HTTPStatus.OK
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas de estados: {e}")
            return {"error": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    def obtener_estadisticas_diarias(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del día
        
        Returns:
            Dict[str, Any]: Estadísticas diarias
        """
        return self.repository.get_statistics_for_period(hours=24)

    def get_alertas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener alertas recientes (lecturas en estado de sequía o inundación)
        
        Args:
            limit: Número máximo de alertas a obtener
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas
        """
        try:
            # Obtener lecturas de alerta (sequía o inundación)
            lecturas_sequia = self.repository.find_by_estado("sequía")
            lecturas_inundacion = self.repository.find_by_estado("inundación")
            
            # Combinar y ordenar por timestamp
            todas_alertas = []
            for lectura in lecturas_sequia:
                todas_alertas.append({
                    "_id": str(lectura.id),
                    "nivel_agua": lectura.nivel_agua,
                    "estado": lectura.estado,
                    "timestamp": lectura.timestamp,
                    "tipo": "sequía"
                })
            
            for lectura in lecturas_inundacion:
                todas_alertas.append({
                    "_id": str(lectura.id),
                    "nivel_agua": lectura.nivel_agua,
                    "estado": lectura.estado,
                    "timestamp": lectura.timestamp,
                    "tipo": "inundación"
                })
            
            # Ordenar por timestamp descendente y limitar
            todas_alertas.sort(key=lambda x: x["timestamp"], reverse=True)
            return todas_alertas[:limit]
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo alertas: {e}")
            return []

    def get_estado_sistema(self) -> Dict[str, Any]:
        """
        Obtener estado general del sistema
        
        Returns:
            Dict[str, Any]: Estado del sistema
        """
        try:
            # Obtener última lectura
            ultima_lectura = self.get_ultima_lectura()
            
            # Obtener estadísticas básicas
            estadisticas = self.obtener_estadisticas_diarias()
            
            # Verificar health de componentes
            db_healthy = self.health_check()
            blockchain_healthy = self.blockchain.validate_chain()
            
            # Determinar estado general
            if db_healthy and blockchain_healthy:
                estado_general = "operativo"
            elif db_healthy or blockchain_healthy:
                estado_general = "degradado"
            else:
                estado_general = "error"
            
            return {
                "estado": estado_general,
                "ultima_lectura": {
                    "_id": str(ultima_lectura.id) if ultima_lectura else None,
                    "nivel_agua": ultima_lectura.nivel_agua if ultima_lectura else None,
                    "estado": ultima_lectura.estado if ultima_lectura else None,
                    "timestamp": ultima_lectura.timestamp if ultima_lectura else None
                },
                "estadisticas": estadisticas,
                "componentes": {
                    "base_datos": "ok" if db_healthy else "error",
                    "blockchain": "ok" if blockchain_healthy else "error"
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estado del sistema: {e}")
            return {
                "estado": "error",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def health_check(self) -> bool:
        """
        Verificar estado del servicio
        
        Returns:
            bool: True si el servicio está saludable
        """
        return self.repository.health_check()
    
    def _determinar_estado(self, nivel_agua: float) -> str:
        """
        Determinar el estado basado en el nivel de agua
        
        Args:
            nivel_agua: Nivel de agua en centímetros
            
        Returns:
            str: Estado del nivel
        """
        if nivel_agua <= 3.5:
            return "inundación"
        elif nivel_agua >= 10:
            return "sequía"
        else:
            return "normal"

    # =============================================================================
    # NUEVOS MÉTODOS PARA DATOS ESTRUCTURADOS DEL ARDUINO
    # =============================================================================

    def guardar_lectura_arduino(self, lectura_data: LecturaArduinoRequest) -> Optional[Dict[str, Any]]:
        """
        Guardar una lectura estructurada del Arduino en MongoDB
        
        Args:
            lectura_data: Datos validados de la lectura del Arduino
            
        Returns:
            Optional[Dict]: Documento guardado o None si falla
        """
        try:
            current_app.logger.info(f"Guardando lectura Arduino en colección lecturas_sensor")
            
            # Preparar documento para MongoDB
            documento = {
                "nivel_cm": lectura_data.nivel_cm,
                "estado": lectura_data.estado,
                "intervalo_ms": lectura_data.intervalo_ms,
                "velocidad_cm_por_s": lectura_data.velocidad_cm_por_s,
                "timestamp": lectura_data.timestamp,
                "created_at": datetime.utcnow().isoformat() + 'Z'
            }
            
            # Guardar usando el repositorio
            documento_guardado = self.repository.guardar_lectura_arduino(documento)
            
            if documento_guardado:
                current_app.logger.info(f"Lectura Arduino guardada con ID: {documento_guardado['_id']}")
                return documento_guardado
            else:
                current_app.logger.error("Error guardando lectura Arduino")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error en guardar_lectura_arduino: {e}")
            return None

    def consultar_lecturas_arduino(self, limit: int = 100, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Consultar lecturas del Arduino con filtros opcionales
        
        Args:
            limit: Límite de resultados (default: 100)
            since: Timestamp de inicio en formato ISO 8601
            
        Returns:
            List[Dict]: Lista de lecturas ordenadas por timestamp desc
        """
        try:
            current_app.logger.info(f"Consultando lecturas Arduino: limit={limit}, since={since}")
            
            # Consultar usando el repositorio
            lecturas = self.repository.consultar_lecturas_arduino(limit=limit, since=since)
            
            current_app.logger.info(f"Encontradas {len(lecturas)} lecturas Arduino")
            return lecturas
            
        except Exception as e:
            current_app.logger.error(f"Error consultando lecturas Arduino: {e}")
            return []
