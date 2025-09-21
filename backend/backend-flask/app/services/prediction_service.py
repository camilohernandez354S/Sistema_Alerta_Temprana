"""
Servicio especializado en predicciones de IA
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from typing import List, Dict, Any
from flask import current_app

from app.models.sensor_model import SensorDocumentObtenido

class PredictionService:
    """Servicio para generar predicciones usando modelos de IA"""
    
    def __init__(self):
        """Inicializar servicio de predicciones"""
        current_app.logger.info("PredictionService inicializado")
    
    def generar_predicciones(self, datos: List[SensorDocumentObtenido]) -> List[Dict[str, Any]]:
        """
        Generar predicciones usando un modelo de IA
        
        Args:
            datos: Datos históricos
            
        Returns:
            List[Dict[str, Any]]: Lista de predicciones
        """
        try:
            if len(datos) < 5:
                current_app.logger.warning("Datos insuficientes para predicciones")
                return self._predicciones_por_defecto()
            
            # Convertir datos a DataFrame
            df = self._preparar_datos(datos)
            
            if df.empty:
                return self._predicciones_por_defecto()
            
            # Entrenar modelo
            model = self._entrenar_modelo(df)
            
            # Generar predicciones
            predicciones = self._generar_predicciones_modelo(model, df, datos)
            
            current_app.logger.info(f"Predicciones generadas para {len(predicciones)} períodos")
            return predicciones
            
        except Exception as e:
            current_app.logger.error(f"Error generando predicciones: {e}")
            return self._predicciones_por_defecto()
    
    def _preparar_datos(self, datos: List[SensorDocumentObtenido]) -> pd.DataFrame:
        """
        Preparar datos para el modelo
        
        Args:
            datos: Datos crudos
            
        Returns:
            pd.DataFrame: Datos preparados
        """
        try:
            df_data = []
            for doc in datos:
                df_data.append({
                    'timestamp': pd.to_datetime(doc.timestamp),
                    'nivel_agua': float(doc.nivel_agua)
                })
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('timestamp')
            df = df.dropna()
            
            return df
        except Exception as e:
            current_app.logger.error(f"Error preparando datos: {e}")
            return pd.DataFrame()
    
    def _entrenar_modelo(self, df: pd.DataFrame) -> LinearRegression:
        """
        Entrenar modelo de regresión lineal
        
        Args:
            df: DataFrame con datos
            
        Returns:
            LinearRegression: Modelo entrenado
        """
        # Preparar features (timestamp como número)
        X = df['timestamp'].astype(np.int64) // 10**9  # Segundos desde epoch
        X = X.values.reshape(-1, 1)
        y = df['nivel_agua'].values
        
        # Entrenar modelo
        model = LinearRegression()
        model.fit(X, y)
        
        return model
    
    def _generar_predicciones_modelo(
        self, 
        model: LinearRegression, 
        df: pd.DataFrame, 
        datos_originales: List[SensorDocumentObtenido]
    ) -> List[Dict[str, Any]]:
        """
        Generar predicciones usando el modelo entrenado
        
        Args:
            model: Modelo entrenado
            df: DataFrame con datos históricos
            datos_originales: Datos originales para comparación
            
        Returns:
            List[Dict[str, Any]]: Lista de predicciones
        """
        # Calcular estadísticas
        media = df['nivel_agua'].mean()
        desviacion = df['nivel_agua'].std()
        ultimo_nivel = datos_originales[-1].nivel_agua
        
        # Timestamps futuros
        timestamp_24h = pd.Timestamp.now() + pd.Timedelta(days=1)
        timestamp_7d = pd.Timestamp.now() + pd.Timedelta(days=7)
        
        # Predicciones
        nivel_24h = model.predict([[timestamp_24h.timestamp()]])[0]
        nivel_7d = model.predict([[timestamp_7d.timestamp()]])[0]
        
        # Calcular probabilidades
        prob_24h = self._calcular_probabilidades(nivel_24h, media, desviacion)
        prob_7d = self._calcular_probabilidades(nivel_7d, media, desviacion)
        
        return [
            {
                "periodo": "24h",
                "porcentaje": prob_24h['inundacion'],
                "fecha": timestamp_24h.isoformat(),
                "tendencia": self._determinar_tendencia(nivel_24h, ultimo_nivel),
                "nivel_predicho": round(nivel_24h, 2),
                "probabilidad_inundacion": prob_24h['inundacion'],
                "probabilidad_sequia": prob_24h['sequia'],
                "probabilidad_normal": prob_24h['normal'],
                "confianza": self._calcular_confianza(len(datos_originales))
            },
            {
                "periodo": "7d",
                "porcentaje": prob_7d['inundacion'],
                "fecha": timestamp_7d.isoformat(),
                "tendencia": self._determinar_tendencia(nivel_7d, ultimo_nivel),
                "nivel_predicho": round(nivel_7d, 2),
                "probabilidad_inundacion": prob_7d['inundacion'],
                "probabilidad_sequia": prob_7d['sequia'],
                "probabilidad_normal": prob_7d['normal'],
                "confianza": self._calcular_confianza(len(datos_originales))
            }
        ]
    
    def _calcular_probabilidades(self, nivel: float, media: float, desviacion: float) -> Dict[str, float]:
        """
        Calcular probabilidades para cada estado
        
        Args:
            nivel: Nivel predicho
            media: Media histórica
            desviacion: Desviación estándar
            
        Returns:
            Dict[str, float]: Probabilidades por estado
        """
        # Constantes de umbral
        NIVEL_SEQUIA = 10.0
        NIVEL_INUNDACION = 3.5
        
        # Inicializar probabilidades
        prob_sequia = 0.0
        prob_inundacion = 0.0
        prob_normal = 0.0
        
        # Calcular probabilidades basadas en umbrales y distribución
        if nivel >= NIVEL_SEQUIA:
            prob_sequia = 90.0
        elif nivel > NIVEL_SEQUIA - desviacion:
            prob_sequia = ((nivel - (NIVEL_SEQUIA - desviacion)) / desviacion) * 70.0
        
        if nivel <= NIVEL_INUNDACION:
            prob_inundacion = 90.0
        elif nivel < NIVEL_INUNDACION + desviacion:
            prob_inundacion = ((NIVEL_INUNDACION + desviacion - nivel) / desviacion) * 70.0
        
        # Probabilidad normal es lo que queda
        if NIVEL_INUNDACION < nivel < NIVEL_SEQUIA:
            prob_normal = 80.0
        
        # Normalizar para que sumen 100%
        total = prob_sequia + prob_inundacion + prob_normal
        if total == 0:
            prob_normal = 100.0
            total = 100.0
        
        return {
            'sequia': round((prob_sequia / total) * 100, 2),
            'inundacion': round((prob_inundacion / total) * 100, 2),
            'normal': round((prob_normal / total) * 100, 2)
        }
    
    def _determinar_tendencia(self, nivel_futuro: float, nivel_actual: float) -> str:
        """
        Determinar tendencia entre dos niveles
        
        Args:
            nivel_futuro: Nivel predicho
            nivel_actual: Nivel actual
            
        Returns:
            str: Tendencia ('subiendo', 'bajando', 'estable')
        """
        diferencia = abs(nivel_futuro - nivel_actual)
        
        if diferencia < 0.1:  # Margen de error pequeño
            return "estable"
        elif nivel_futuro > nivel_actual:
            return "subiendo"
        else:
            return "bajando"
    
    def _calcular_confianza(self, num_datos: int) -> float:
        """
        Calcular nivel de confianza basado en cantidad de datos
        
        Args:
            num_datos: Número de puntos de datos
            
        Returns:
            float: Nivel de confianza (0.0 - 1.0)
        """
        if num_datos < 10:
            return 0.3
        elif num_datos < 50:
            return 0.6
        elif num_datos < 100:
            return 0.8
        else:
            return 0.9
    
    def _predicciones_por_defecto(self) -> List[Dict[str, Any]]:
        """
        Predicciones por defecto cuando no hay suficientes datos
        
        Returns:
            List[Dict[str, Any]]: Predicciones por defecto
        """
        timestamp_24h = pd.Timestamp.now() + pd.Timedelta(days=1)
        timestamp_7d = pd.Timestamp.now() + pd.Timedelta(days=7)
        
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
