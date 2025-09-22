"""
Servicio especializado en predicciones robustas con limpieza de datos y señales
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app

from app.models.sensor_model import SensorDocumentObtenido
from app.utils.logging_config import PredictionLogger

# Importación opcional de scikit-learn para mejor precisión
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class PredictionService:
    """
    Servicio para generar predicciones robustas con preprocesamiento avanzado
    
    Características principales:
    - Ventana móvil de datos históricos para suavizar ruido
    - Suavizado exponencial y media móvil
    - Detección y eliminación de outliers usando IQR
    - Regresión lineal con numpy.polyfit o scikit-learn
    - Ajuste de confianza basado en R² y cantidad de datos
    - Predicciones multi-horizonte con factor de amortiguación
    - Clasificación de estados configurables
    """
    
    def __init__(self):
        """Inicializar servicio de predicciones"""
        self.config = current_app.config
        self.prediction_logger = PredictionLogger()
        current_app.logger.info(f"PredictionService inicializado - scikit-learn: {'disponible' if SKLEARN_AVAILABLE else 'no disponible'}")
    
    def generar_predicciones_multi_horizonte(
        self, 
        datos: List[SensorDocumentObtenido],
        horizons: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Generar predicciones multi-horizonte con limpieza de datos
        
        Args:
            datos: Datos históricos del sensor
            horizons: Lista de horizontes en minutos (default: config)
            
        Returns:
            Dict con estructura completa de predicciones
        """
        try:
            if horizons is None:
                horizons = self.config.get('DEFAULT_HORIZONS', [30, 60, 120, 180])
            
            window_minutes = self.config.get('REGRESSION_WINDOW_MIN', 180)  # 3 horas por defecto
            min_data_points = self.config.get('PREDICTION_MIN_DATA_POINTS', 10)
            
            # Log inicio de predicción
            self.prediction_logger.log_prediction_start(
                data_points=len(datos),
                horizons=horizons,
                window_minutes=window_minutes
            )
            
            # 1. Preprocesamiento y limpieza de datos
            datos_limpios = self._preprocesar_datos_avanzado(datos, window_minutes)
            
            if len(datos_limpios) < min_data_points:
                self.prediction_logger.log_warning_insufficient_data(
                    available_points=len(datos_limpios),
                    required_points=min_data_points
                )
                return self._respuesta_prediccion_fallback(horizons)
            
            # 2. Análisis de señales con ventana móvil
            analisis_senales = self._analizar_senales_ventana_movil(datos_limpios, window_minutes)
            
            # 3. Generar predicciones multi-horizonte
            predicciones = []
            for horizon in horizons:
                pred = self._generar_prediccion_horizonte_avanzada(
                    datos_limpios, analisis_senales, horizon
                )
                predicciones.append(pred)
                
                # Log resultado individual
                self.prediction_logger.log_prediction_result(
                    horizon=horizon,
                    predicted_level=pred['nivel_cm'],
                    confidence=pred['confianza'],
                    state=pred['estado']
                )
            
            # 4. Información del estado actual
            nivel_actual = datos_limpios[-1]['nivel_cm']
            tendencia_actual = analisis_senales['tendencia']
            pendiente_actual = analisis_senales['pendiente_cm_por_h']
            r2 = analisis_senales['r_squared']
            
            resultado = {
                "meta": {
                    "generated_at": datetime.now().isoformat(),
                    "window_minutes": window_minutes,
                    "r2": round(r2, 3),
                    "points_used": len(datos_limpios),
                    "horizons": horizons,
                    "sklearn_used": SKLEARN_AVAILABLE,
                    "intervalo_ms": self._obtener_intervalo_promedio(datos_limpios)
                },
                "current": {
                    "nivel_cm": round(nivel_actual, 1),
                    "estado": self._classify_level(nivel_actual),
                    "tendencia": tendencia_actual,
                    "pendiente_cm_por_h": round(pendiente_actual, 1)
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
            
            current_app.logger.info(f"Predicciones generadas exitosamente - R²: {r2:.3f}, Confianza promedio: {avg_confidence:.3f}")
            return resultado
            
        except Exception as e:
            self.prediction_logger.log_error_prediction(str(e))
            current_app.logger.error(f"Error generando predicciones: {e}")
            return self._respuesta_error_prediccion(str(e))
    
    def _preprocesar_datos_avanzado(self, datos: List[SensorDocumentObtenido], window_minutes: int) -> List[Dict[str, Any]]:
        """
        Preprocesamiento avanzado de datos con múltiples técnicas de limpieza
        
        Proceso:
        1. Validación de esquema y conversión de tipos
        2. Ordenamiento temporal
        3. Eliminación de outliers usando IQR
        4. Interpolación de huecos pequeños
        5. Suavizado exponencial
        6. Aplicación de ventana móvil
        
        Args:
            datos: Datos crudos del sensor
            window_minutes: Ventana temporal para análisis
            
        Returns:
            Lista de datos limpios y suavizados
        """
        try:
            current_app.logger.info(f"🔄 Iniciando preprocesamiento avanzado de {len(datos)} registros")
            
            # 1. Validación de esquema y conversión
            datos_validos = []
            for doc in datos:
                try:
                    nivel_cm = float(doc.nivel_agua)
                    timestamp = datetime.fromisoformat(doc.timestamp.replace('Z', '+00:00'))
                    
                    # Validación de rangos razonables
                    if 0 <= nivel_cm <= 200:  # Rango máximo razonable para niveles de agua
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
            
            # 2. Ordenamiento temporal
            datos_validos.sort(key=lambda x: x['timestamp'])
            
            # 3. Eliminación de outliers usando IQR
            current_app.logger.debug(f"Aplicando detección de outliers a {len(datos_validos)} registros válidos")
            datos_sin_outliers = self._eliminar_outliers_iqr(datos_validos)
            outliers_removed = len(datos_validos) - len(datos_sin_outliers)
            if outliers_removed > 0:
                current_app.logger.info(f"📊 Outliers removidos: {outliers_removed} de {len(datos_validos)} registros ({outliers_removed/len(datos_validos)*100:.1f}%)")
            
            # 4. Interpolación de huecos temporales
            datos_completos = self._interpolar_huecos_temporales(datos_sin_outliers)
            
            # 5. Suavizado exponencial
            datos_suavizados = self._aplicar_suavizado_exponencial(datos_completos)
            
            # 6. Aplicar ventana móvil para análisis
            cutoff_time = datos_suavizados[-1]['timestamp'] - timedelta(minutes=window_minutes)
            datos_ventana = [d for d in datos_suavizados if d['timestamp'] >= cutoff_time]
            
            # Si no hay suficientes datos en la ventana, usar todos
            if len(datos_ventana) < 5:
                datos_ventana = datos_suavizados
            
            # Log preprocesamiento
            self.prediction_logger.log_data_preprocessing(
                original_count=len(datos),
                cleaned_count=len(datos_ventana),
                outliers_removed=outliers_removed
            )
            
            current_app.logger.info(f"✅ Preprocesamiento completado: {len(datos)} → {len(datos_ventana)} registros finales")
            current_app.logger.debug(f"Detalles: {len(datos)} originales → {len(datos_validos)} válidos → {len(datos_sin_outliers)} sin outliers → {len(datos_ventana)} en ventana temporal")
            return datos_ventana
            
        except Exception as e:
            current_app.logger.error(f"Error en preprocesamiento avanzado: {e}")
            return []
    
    def _eliminar_outliers_iqr(self, datos: List[Dict]) -> List[Dict]:
        """
        Eliminar outliers usando el rango intercuartílico (IQR)
        
        Método robusto para detectar valores anómalos basado en la distribución
        de los datos sin asumir una distribución normal.
        """
        try:
            if len(datos) < 4:
                return datos
            
            niveles = [d['nivel_cm'] for d in datos]
            
            # Calcular cuartiles
            q1 = np.percentile(niveles, 25)
            q3 = np.percentile(niveles, 75)
            iqr = q3 - q1
            
            # Fence extendido para mayor robustez
            lower_fence = q1 - 2.0 * iqr  # Más conservador que 1.5
            upper_fence = q3 + 2.0 * iqr
            
            datos_limpios = []
            outliers_removidos = 0
            
            for dato in datos:
                if lower_fence <= dato['nivel_cm'] <= upper_fence:
                    datos_limpios.append(dato)
                else:
                    outliers_removidos += 1
            
            if outliers_removidos > 0:
                current_app.logger.info(f"Removidos {outliers_removidos} outliers usando IQR (fence: {lower_fence:.1f} - {upper_fence:.1f})")
            
            return datos_limpios
            
        except Exception as e:
            current_app.logger.warning(f"Error eliminando outliers: {e}")
            return datos
    
    def _interpolar_huecos_temporales(self, datos: List[Dict]) -> List[Dict]:
        """
        Interpolar huecos temporales pequeños usando interpolación lineal
        
        Solo interpola huecos menores a 2 horas para mantener la integridad
        de los datos y evitar predicciones artificiales.
        """
        try:
            if len(datos) < 2:
                return datos
            
            datos_completos = []
            for i, dato in enumerate(datos):
                datos_completos.append(dato)
                
                # Verificar si hay hueco con el siguiente punto
                if i < len(datos) - 1:
                    next_dato = datos[i + 1]
                    diff_minutes = (next_dato['timestamp'] - dato['timestamp']).total_seconds() / 60
                    
                    # Solo interpolar huecos entre 15 minutos y 2 horas
                    if 15 < diff_minutes < 120:
                        num_puntos = min(int(diff_minutes / 15), 8)  # Máximo 8 puntos interpolados
                        for j in range(1, num_puntos):
                            timestamp_interp = dato['timestamp'] + timedelta(minutes=j * (diff_minutes / num_puntos))
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
            current_app.logger.warning(f"Error en interpolación temporal: {e}")
            return datos
    
    def _aplicar_suavizado_exponencial(self, datos: List[Dict], alpha: float = 0.3) -> List[Dict]:
        """
        Aplicar suavizado exponencial para reducir ruido de alta frecuencia
        
        El suavizado exponencial es más efectivo que la media móvil para
        datos con tendencias, ya que da más peso a observaciones recientes.
        
        Args:
            datos: Datos a suavizar
            alpha: Factor de suavizado (0.1 = más suave, 0.5 = menos suave)
        """
        try:
            if len(datos) < 3:
                return datos
            
            datos_suavizados = []
            niveles = [d['nivel_cm'] for d in datos]
            
            # Inicializar con el primer valor
            suavizado = niveles[0]
            datos_suavizados.append({
                'id': datos[0]['id'],
                'nivel_cm': suavizado,
                'timestamp': datos[0]['timestamp']
            })
            
            # Aplicar suavizado exponencial
            for i in range(1, len(datos)):
                suavizado = alpha * niveles[i] + (1 - alpha) * suavizado
                datos_suavizados.append({
                    'id': datos[i]['id'],
                    'nivel_cm': suavizado,
                    'timestamp': datos[i]['timestamp']
                })
            
            return datos_suavizados
            
        except Exception as e:
            current_app.logger.warning(f"Error aplicando suavizado exponencial: {e}")
            return datos
    
    def _analizar_senales_ventana_movil(self, datos: List[Dict], window_minutes: int) -> Dict[str, Any]:
        """
        Análisis de señales usando ventana móvil con regresión lineal
        
        Calcula la pendiente, R² y tendencia usando una ventana temporal
        de los datos más recientes para mayor precisión.
        
        Args:
            datos: Datos preprocesados
            window_minutes: Ventana temporal en minutos
            
        Returns:
            Dict con análisis de señales
        """
        try:
            # Usar ventana móvil de los datos más recientes
            cutoff_time = datos[-1]['timestamp'] - timedelta(minutes=window_minutes)
            datos_ventana = [d for d in datos if d['timestamp'] >= cutoff_time]
            
            # Si no hay suficientes datos en la ventana, usar todos
            if len(datos_ventana) < 3:
                datos_ventana = datos
                window_actual = (datos[-1]['timestamp'] - datos[0]['timestamp']).total_seconds() / 60
            else:
                window_actual = window_minutes
            
            # Preparar datos para regresión
            timestamps_numeric = [(d['timestamp'] - datos_ventana[0]['timestamp']).total_seconds() / 3600 
                                for d in datos_ventana]  # Convertir a horas
            niveles = [d['nivel_cm'] for d in datos_ventana]
            
            if len(timestamps_numeric) >= 2:
                if SKLEARN_AVAILABLE:
                    # Usar scikit-learn para mayor precisión
                    X = np.array(timestamps_numeric).reshape(-1, 1)
                    y = np.array(niveles)
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    pendiente_cm_por_h = model.coef_[0]
                    r_squared = model.score(X, y)
                    
                else:
                    # Usar numpy.polyfit como fallback
                    slope, intercept = np.polyfit(timestamps_numeric, niveles, 1)
                    pendiente_cm_por_h = slope
                    
                    # Calcular R² manualmente
                    y_pred = [slope * t + intercept for t in timestamps_numeric]
                    ss_res = sum((niveles[i] - y_pred[i]) ** 2 for i in range(len(niveles)))
                    ss_tot = sum((n - np.mean(niveles)) ** 2 for n in niveles)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            else:
                pendiente_cm_por_h = 0
                r_squared = 0
            
            # Determinar tendencia basada en pendiente y confianza
            if abs(pendiente_cm_por_h) < 0.5 or r_squared < 0.3:
                tendencia = "estable"
            elif pendiente_cm_por_h > 0:
                tendencia = "sube"
            else:
                tendencia = "baja"
            
            resultado = {
                'pendiente_cm_por_h': pendiente_cm_por_h,
                'tendencia': tendencia,
                'r_squared': max(0, min(1, r_squared)),  # Clamp entre 0 y 1
                'window_minutes': window_actual,
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
    
    def _generar_prediccion_horizonte_avanzada(
        self, 
        datos: List[Dict], 
        analisis_senales: Dict[str, Any], 
        horizon_minutes: int
    ) -> Dict[str, Any]:
        """
        Generar predicción para un horizonte específico con ajuste de confianza
        
        Usa el nivel actual y la pendiente calculada, aplicando un factor de
        amortiguación que depende de la confianza del modelo.
        
        Args:
            datos: Datos preprocesados
            analisis_senales: Análisis de señales y tendencias
            horizon_minutes: Horizonte temporal en minutos
            
        Returns:
            Predicción para el horizonte específico
        """
        try:
            nivel_actual = datos[-1]['nivel_cm']
            pendiente = analisis_senales['pendiente_cm_por_h']
            r_squared = analisis_senales['r_squared']
            puntos_ventana = analisis_senales['data_points_window']
            
            # Calcular confianza basada en R² y cantidad de datos
            confianza_base = r_squared
            confianza_densidad = min(1.0, puntos_ventana / 30)  # Máximo con 30 puntos
            confianza = (confianza_base * 0.7 + confianza_densidad * 0.3)
            
            # Limitar confianza entre 0.3 y 0.95
            confianza = max(0.3, min(0.95, confianza))
            
            # Factor de amortiguación basado en confianza
            # Si la confianza es baja o la tendencia es débil, aplanar predicciones
            if confianza < 0.5 or abs(pendiente) < 1.0:
                factor_amortiguacion = 0.3  # Muy conservador
            elif confianza < 0.7:
                factor_amortiguacion = 0.5  # Moderado
            else:
                factor_amortiguacion = 0.7  # Más agresivo
            
            # Predicción lineal amortiguada
            horizon_hours = horizon_minutes / 60
            nivel_predicho = nivel_actual + (pendiente * horizon_hours * factor_amortiguacion)
            
            # Evitar valores negativos
            nivel_predicho = max(0, nivel_predicho)
            
            return {
                "horizon_min": horizon_minutes,
                "nivel_cm": round(nivel_predicho, 1),
                "estado": self._classify_level(nivel_predicho),
                "confianza": round(confianza, 2)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generando predicción para horizonte {horizon_minutes}: {e}")
            return {
                "horizon_min": horizon_minutes,
                "nivel_cm": 0.0,
                "estado": "Normal",
                "confianza": 0.3
            }
    
    def _classify_level(self, nivel_cm: float) -> str:
        """
        Clasificar nivel de agua según umbrales configurables
        
        Args:
            nivel_cm: Nivel en centímetros
            
        Returns:
            Estado clasificado: "Sequía", "Normal", o "Inundación"
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
                "window_minutes": 0,
                "r2": 0.0,
                "points_used": 0,
                "horizons": horizons,
                "sklearn_used": SKLEARN_AVAILABLE,
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
                    "confianza": 0.3
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

    def _obtener_intervalo_promedio(self, datos: List[Dict]) -> Optional[int]:
        """
        Obtener el intervalo promedio de muestreo de los datos
        
        Args:
            datos: Lista de datos con posible campo intervalo_ms
            
        Returns:
            Optional[int]: Intervalo promedio en milisegundos o None si no disponible
        """
        try:
            intervalos = []
            for dato in datos:
                if 'intervalo_ms' in dato and dato['intervalo_ms'] is not None:
                    intervalos.append(dato['intervalo_ms'])
            
            if intervalos:
                return int(sum(intervalos) / len(intervalos))
            else:
                return None
                
        except Exception:
            return None