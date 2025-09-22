"""
Servicio especializado en predicciones robustas con limpieza de datos y señales
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app

from app.models.sensor_model import SensorDocumentObtenido
from app.utils.logging_config import PredictionLogger


class PredictionService:
    """Servicio para generar predicciones robustas con preprocesamiento avanzado"""
    
    def __init__(self):
        """Inicializar servicio de predicciones"""
        self.config = current_app.config
        self.prediction_logger = PredictionLogger()
        current_app.logger.info("PredictionService inicializado con configuración robusta")
    
    def generar_predicciones_multi_horizonte(
        self, 
        datos: List[SensorDocumentObtenido],
        horizons: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Generar predicciones multi-horizonte con limpieza de datos
        
        Args:
            datos: Datos históricos
            horizons: Lista de horizontes en minutos (default: config)
            
        Returns:
            Dict con predicciones estructuradas
        """
        try:
            if horizons is None:
                horizons = self.config.get('DEFAULT_HORIZONS', [30, 60, 180])
            
            window_minutes = self.config.get('REGRESSION_WINDOW_MIN', 120)
            
            # Log inicio de predicción
            self.prediction_logger.log_prediction_start(
                data_points=len(datos),
                horizons=horizons,
                window_minutes=window_minutes
            )
            
            # 1. Preprocesamiento y limpieza
            datos_limpios = self._preprocesar_datos(datos)
            
            if len(datos_limpios) < self.config.get('PREDICTION_MIN_DATA_POINTS', 10):
                self.prediction_logger.log_warning_insufficient_data(
                    available_points=len(datos_limpios),
                    required_points=self.config.get('PREDICTION_MIN_DATA_POINTS', 10)
                )
                return self._respuesta_prediccion_fallback(horizons)
            
            # 2. Análisis de señales y tendencias
            senales = self._analizar_senales(datos_limpios)
            
            # 3. Generar predicciones
            predicciones = []
            for horizon in horizons:
                pred = self._generar_prediccion_horizonte(
                    datos_limpios, senales, horizon
                )
                predicciones.append(pred)
                
                # Log resultado individual
                self.prediction_logger.log_prediction_result(
                    horizon=horizon,
                    predicted_level=pred['nivel_cm'],
                    confidence=pred['confianza'],
                    state=pred['estado']
                )
            
            # 4. Información actual
            nivel_actual = datos_limpios[-1]['nivel_cm']
            tendencia_actual = senales['tendencia']
            pendiente_actual = senales['pendiente_cm_por_h']
            
            resultado = {
                "meta": {
                    "generated_at": datetime.now().isoformat(),
                    "window_used_minutes": senales['window_minutes'],
                    "horizons": horizons,
                    "data_points_used": len(datos_limpios)
                },
                "current": {
                    "nivel_cm": round(nivel_actual, 2),
                    "estado": self._classify_level(nivel_actual),
                    "tendencia": tendencia_actual,
                    "pendiente_cm_por_h": round(pendiente_actual, 2)
                },
                "predicciones": predicciones
            }
            
            # Log completación
            avg_confidence = np.mean([p['confianza'] for p in predicciones])
            self.prediction_logger.log_prediction_complete(
                total_horizons=len(horizons),
                avg_confidence=avg_confidence,
                processing_time=0.0  # TODO: implementar timing
            )
            
            current_app.logger.info(f"Predicciones generadas exitosamente para {len(horizons)} horizontes")
            return resultado
            
        except Exception as e:
            self.prediction_logger.log_error_prediction(str(e))
            current_app.logger.error(f"Error generando predicciones: {e}")
            return self._respuesta_error_prediccion(str(e))
    
    def _preprocesar_datos(self, datos: List[SensorDocumentObtenido]) -> List[Dict[str, Any]]:
        """
        Preprocesamiento robusto de datos con validación y limpieza
        
        Args:
            datos: Datos crudos
            
        Returns:
            Lista de datos limpios y validados
        """
        try:
            # 1. Validar esquema y convertir
            datos_validos = []
            for doc in datos:
                try:
                    # Validar esquema requerido
                    nivel_cm = float(doc.nivel_agua)
                    timestamp = datetime.fromisoformat(doc.timestamp.replace('Z', '+00:00'))
                    
                    datos_validos.append({
                        'id': str(doc.id),
                        'nivel_cm': nivel_cm,
                        'timestamp': timestamp
                    })
                except (ValueError, TypeError, AttributeError) as e:
                    current_app.logger.warning(f"Registro inválido omitido: {e}")
                    continue
            
            if not datos_validos:
                return []
            
            # 2. Ordenar por timestamp
            datos_validos.sort(key=lambda x: x['timestamp'])
            
            # 3. Quitar outliers con IQR
            niveles = [d['nivel_cm'] for d in datos_validos]
            datos_sin_outliers = self._remover_outliers_iqr(datos_validos, niveles)
            
            # 4. Rellenar huecos con interpolación
            datos_completos = self._interpolar_huecos(datos_sin_outliers)
            
            # 5. Suavizar con media móvil
            datos_suavizados = self._aplicar_media_movil(datos_completos, window=5)
            
            # Log preprocesamiento
            outliers_removed = len(datos) - len(datos_sin_outliers)
            self.prediction_logger.log_data_preprocessing(
                original_count=len(datos),
                cleaned_count=len(datos_suavizados),
                outliers_removed=outliers_removed
            )
            
            current_app.logger.info(f"Datos preprocesados: {len(datos)} -> {len(datos_suavizados)}")
            return datos_suavizados
            
        except Exception as e:
            current_app.logger.error(f"Error en preprocesamiento: {e}")
            return []
    
    def _remover_outliers_iqr(self, datos: List[Dict], niveles: List[float]) -> List[Dict]:
        """Remover outliers usando método IQR"""
        try:
            if len(niveles) < 4:
                return datos
            
            q1 = np.percentile(niveles, 25)
            q3 = np.percentile(niveles, 75)
            iqr = q3 - q1
            
            # Fence simple
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr
            
            datos_limpios = []
            outliers_removidos = 0
            
            for dato in datos:
                if lower_fence <= dato['nivel_cm'] <= upper_fence:
                    datos_limpios.append(dato)
                else:
                    outliers_removidos += 1
            
            if outliers_removidos > 0:
                current_app.logger.info(f"Removidos {outliers_removidos} outliers usando IQR")
            
            return datos_limpios
            
        except Exception as e:
            current_app.logger.warning(f"Error removiendo outliers: {e}")
            return datos
    
    def _interpolar_huecos(self, datos: List[Dict]) -> List[Dict]:
        """Rellenar pequeños huecos con interpolación lineal"""
        try:
            if len(datos) < 2:
                return datos
            
            datos_completos = []
            for i, dato in enumerate(datos):
                datos_completos.append(dato)
                
                # Verificar si hay hueco significativo con el siguiente punto
                if i < len(datos) - 1:
                    next_dato = datos[i + 1]
                    diff_minutes = (next_dato['timestamp'] - dato['timestamp']).total_seconds() / 60
                    
                    # Si hay hueco mayor a 30 minutos pero menor a 2 horas, interpolar
                    if 30 < diff_minutes < 120:
                        num_puntos = int(diff_minutes / 15)  # Un punto cada 15 minutos
                        for j in range(1, num_puntos):
                            timestamp_interp = dato['timestamp'] + timedelta(minutes=j * 15)
                            nivel_interp = np.interp(
                                j / num_puntos,
                                [0, 1],
                                [dato['nivel_cm'], next_dato['nivel_cm']]
                            )
                            datos_completos.append({
                                'id': f"interp_{i}_{j}",
                                'nivel_cm': nivel_interp,
                                'timestamp': timestamp_interp
                            })
            
            return datos_completos
            
        except Exception as e:
            current_app.logger.warning(f"Error en interpolación: {e}")
            return datos
    
    def _aplicar_media_movil(self, datos: List[Dict], window: int = 5) -> List[Dict]:
        """Aplicar media móvil para suavizar ruido"""
        try:
            if len(datos) < window:
                return datos
            
            datos_suavizados = []
            for i in range(len(datos)):
                # Ventana simétrica centrada
                start_idx = max(0, i - window // 2)
                end_idx = min(len(datos), i + window // 2 + 1)
                
                window_data = datos[start_idx:end_idx]
                nivel_promedio = np.mean([d['nivel_cm'] for d in window_data])
                
                datos_suavizados.append({
                    'id': datos[i]['id'],
                    'nivel_cm': nivel_promedio,
                    'timestamp': datos[i]['timestamp']
                })
            
            return datos_suavizados
            
        except Exception as e:
            current_app.logger.warning(f"Error aplicando media móvil: {e}")
            return datos
    
    def _analizar_senales(self, datos: List[Dict]) -> Dict[str, Any]:
        """
        Analizar señales y tendencias
        
        Args:
            datos: Datos preprocesados
            
        Returns:
            Dict con análisis de señales
        """
        try:
            window_minutes = self.config.get('REGRESSION_WINDOW_MIN', 120)
            
            # Usar ventana más reciente para análisis de tendencia
            cutoff_time = datos[-1]['timestamp'] - timedelta(minutes=window_minutes)
            datos_ventana = [d for d in datos if d['timestamp'] >= cutoff_time]
            
            if len(datos_ventana) < 3:
                # Si no hay suficientes datos en la ventana, usar todos
                datos_ventana = datos
                window_minutes = (datos[-1]['timestamp'] - datos[0]['timestamp']).total_seconds() / 60
            
            # Calcular pendiente con polyfit
            timestamps_numeric = [(d['timestamp'] - datos_ventana[0]['timestamp']).total_seconds() / 3600 
                                for d in datos_ventana]  # Convertir a horas
            niveles = [d['nivel_cm'] for d in datos_ventana]
            
            if len(timestamps_numeric) >= 2:
                # Regresión lineal simple
                slope, intercept = np.polyfit(timestamps_numeric, niveles, 1)
                pendiente_cm_por_h = slope
                
                # Calcular R² para confianza
                y_pred = [slope * t + intercept for t in timestamps_numeric]
                ss_res = sum((niveles[i] - y_pred[i]) ** 2 for i in range(len(niveles)))
                ss_tot = sum((n - np.mean(niveles)) ** 2 for n in niveles)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            else:
                pendiente_cm_por_h = 0
                r_squared = 0
            
            # Determinar tendencia
            if abs(pendiente_cm_por_h) < 0.5:
                tendencia = "estable"
            elif pendiente_cm_por_h > 0:
                tendencia = "sube"
            else:
                tendencia = "baja"
            
            resultado = {
                'pendiente_cm_por_h': pendiente_cm_por_h,
                'tendencia': tendencia,
                'r_squared': r_squared,
                'window_minutes': window_minutes,
                'data_points_window': len(datos_ventana)
            }
            
            # Log análisis de señales
            self.prediction_logger.log_signal_analysis(
                slope=pendiente_cm_por_h,
                r_squared=r_squared,
                trend=tendencia,
                window_points=len(datos_ventana)
            )
            
            return resultado
            
        except Exception as e:
            current_app.logger.warning(f"Error analizando señales: {e}")
            return {
                'pendiente_cm_por_h': 0,
                'tendencia': 'estable',
                'r_squared': 0,
                'window_minutes': 0,
                'data_points_window': 0
            }
    
    def _generar_prediccion_horizonte(
        self, 
        datos: List[Dict], 
        senales: Dict[str, Any], 
        horizon_minutes: int
    ) -> Dict[str, Any]:
        """
        Generar predicción para un horizonte específico
        
        Args:
            datos: Datos preprocesados
            senales: Análisis de señales
            horizon_minutes: Horizonte en minutos
            
        Returns:
            Predicción para el horizonte
        """
        try:
            nivel_actual = datos[-1]['nivel_cm']
            pendiente = senales['pendiente_cm_por_h']
            r_squared = senales['r_squared']
            
            # Predicción con factor de amortiguación
            factor_amortiguacion = 0.6
            horizon_hours = horizon_minutes / 60
            
            # Predicción lineal amortiguada
            nivel_predicho = nivel_actual + (pendiente * horizon_hours * factor_amortiguacion)
            
            # Clamp a mínimo 0
            nivel_predicho = max(0, nivel_predicho)
            
            # Calcular confianza
            confianza_base = min(1.0, r_squared)
            confianza_densidad = min(1.0, senales['data_points_window'] / 20)  # Máximo con 20 puntos
            confianza = (confianza_base + confianza_densidad) / 2
            
            return {
                "horizon_min": horizon_minutes,
                "nivel_cm": round(nivel_predicho, 2),
                "estado": self._classify_level(nivel_predicho),
                "confianza": round(confianza, 2)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generando predicción para horizonte {horizon_minutes}: {e}")
            return {
                "horizon_min": horizon_minutes,
                "nivel_cm": 0.0,
                "estado": "Normal",
                "confianza": 0.0
            }
    
    def _classify_level(self, nivel_cm: float) -> str:
        """
        Clasificar nivel según umbrales configurables
        
        Args:
            nivel_cm: Nivel en centímetros
            
        Returns:
            Estado clasificado
        """
        drought_max = self.config.get('DROUGHT_MAX_CM', 20.0)
        normal_max = self.config.get('NORMAL_MAX_CM', 60.0)
        
        if nivel_cm <= drought_max:
            return "Sequía"
        elif nivel_cm >= normal_max:
            return "Inundación"
        else:
            return "Normal"
    
    def _respuesta_prediccion_fallback(self, horizons: List[int]) -> Dict[str, Any]:
        """Respuesta de fallback cuando no hay suficientes datos"""
        return {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "window_used_minutes": 0,
                "horizons": horizons,
                "data_points_used": 0,
                "warning": "Datos insuficientes para predicción robusta"
            },
            "current": {
                "nivel_cm": 0.0,
                "estado": "Normal",
                "tendencia": "estable",
                "pendiente_cm_por_h": 0.0
            },
            "predicciones": [
                {
                    "horizon_min": h,
                    "nivel_cm": 0.0,
                    "estado": "Normal",
                    "confianza": 0.1
                }
                for h in horizons
            ]
        }
    
    def _respuesta_error_prediccion(self, error_msg: str) -> Dict[str, Any]:
        """Respuesta de error estructurada"""
        return {
            "error": {
                "message": f"Error generando predicciones: {error_msg}",
                "code": "PREDICTION_FAILED"
            }
        }
    
    # Métodos de compatibilidad con la implementación anterior
    def generar_predicciones(self, datos: List[SensorDocumentObtenido]) -> List[Dict[str, Any]]:
        """
        Método de compatibilidad con implementación anterior
        Genera predicciones en formato legacy
        """
        try:
            resultado = self.generar_predicciones_multi_horizonte(datos)
            
            if "error" in resultado:
                return self._predicciones_por_defecto()
            
            # Convertir a formato legacy
            predicciones_legacy = []
            for pred in resultado["predicciones"]:
                predicciones_legacy.append({
                    "periodo": f"{pred['horizon_min']}m",
                    "porcentaje": 50.0,  # Valor por defecto
                    "fecha": (datetime.now() + timedelta(minutes=pred['horizon_min'])).isoformat(),
                    "tendencia": resultado["current"]["tendencia"],
                    "nivel_predicho": pred['nivel_cm'],
                    "probabilidad_inundacion": 33.33,
                    "probabilidad_sequia": 33.33,
                    "probabilidad_normal": 33.34,
                    "confianza": pred['confianza']
                })
            
            return predicciones_legacy
            
        except Exception as e:
            current_app.logger.error(f"Error en método de compatibilidad: {e}")
            return self._predicciones_por_defecto()
    
    def _predicciones_por_defecto(self) -> List[Dict[str, Any]]:
        """Predicciones por defecto cuando no hay suficientes datos"""
        timestamp_24h = datetime.now() + timedelta(hours=24)
        timestamp_7d = datetime.now() + timedelta(days=7)
        
        return [
            {
                "periodo": "24h",
                "porcentaje": 33.33,
                "fecha": timestamp_24h.isoformat(),
                "tendencia": "estable",
                "nivel_predicho": 6.5,
                "probabilidad_inundacion": 33.33,
                "probabilidad_sequia": 33.33,
                "probabilidad_normal": 33.34,
                "confianza": 0.1
            },
            {
                "periodo": "7d",
                "porcentaje": 33.33,
                "fecha": timestamp_7d.isoformat(),
                "tendencia": "estable",
                "nivel_predicho": 6.5,
                "probabilidad_inundacion": 33.33,
                "probabilidad_sequia": 33.33,
                "probabilidad_normal": 33.34,
                "confianza": 0.1
            }
        ]