"""
Pruebas para el servicio de predicción mejorado
"""
import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.services.prediction_service import PredictionService
from app.models.sensor_model import SensorDocumentObtenido


class TestPredictionServiceImproved:
    """Pruebas para PredictionService con mejoras avanzadas"""
    
    @pytest.fixture
    def prediction_service(self):
        """Fixture para el servicio de predicción"""
        with patch('app.services.prediction_service.current_app') as mock_app:
            mock_app.config = {
                'DEFAULT_HORIZONS': [30, 60, 120, 180, 360],
                'DROUGHT_MAX_CM': 20.0,
                'NORMAL_MAX_CM': 60.0,
                'REGRESSION_WINDOW_MIN': 180,  # 3 horas
                'PREDICTION_MIN_DATA_POINTS': 10,
                'EXPONENTIAL_SMOOTHING_ALPHA': 0.3,
                'OUTLIER_IQR_FACTOR': 2.0,
                'MIN_CONFIDENCE': 0.3,
                'MAX_CONFIDENCE': 0.95
            }
            mock_app.logger = Mock()
            service = PredictionService()
            return service
    
    @pytest.fixture
    def sample_data_ascending(self):
        """Datos de prueba con tendencia ascendente clara"""
        now = datetime.now()
        data = []
        for i in range(50):
            timestamp = now - timedelta(minutes=i*3)
            nivel = 30.0 + (i * 0.8)  # Tendencia ascendente fuerte
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    @pytest.fixture
    def sample_data_descending(self):
        """Datos de prueba con tendencia descendente clara"""
        now = datetime.now()
        data = []
        for i in range(50):
            timestamp = now - timedelta(minutes=i*3)
            nivel = 80.0 - (i * 0.6)  # Tendencia descendente
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    @pytest.fixture
    def sample_data_stable(self):
        """Datos de prueba con tendencia estable"""
        now = datetime.now()
        data = []
        for i in range(50):
            timestamp = now - timedelta(minutes=i*3)
            nivel = 45.0 + np.sin(i * 0.1) * 2  # Oscilación pequeña alrededor de 45
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    @pytest.fixture
    def sample_data_with_outliers(self):
        """Datos de prueba con outliers significativos"""
        now = datetime.now()
        data = []
        for i in range(50):
            timestamp = now - timedelta(minutes=i*3)
            nivel = 40.0 + np.sin(i * 0.1) * 5  # Datos normales
            # Agregar outliers en posiciones específicas
            if i in [10, 20, 30]:
                nivel += 80  # Outlier grande
            elif i in [15, 25, 35]:
                nivel -= 50  # Outlier negativo
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    @pytest.fixture
    def sample_data_noisy(self):
        """Datos de prueba con ruido de alta frecuencia"""
        now = datetime.now()
        data = []
        for i in range(100):
            timestamp = now - timedelta(minutes=i*2)
            # Tendencia base con ruido
            nivel_base = 35.0 + (i * 0.3)
            noise = np.random.normal(0, 3)  # Ruido significativo
            nivel = nivel_base + noise
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    def test_classify_level_improved(self, prediction_service):
        """Probar clasificación de niveles con umbrales configurables"""
        # Sequía
        assert prediction_service._classify_level(15.0) == "Sequía"
        assert prediction_service._classify_level(20.0) == "Sequía"  # Límite exacto
        
        # Normal
        assert prediction_service._classify_level(25.0) == "Normal"
        assert prediction_service._classify_level(45.0) == "Normal"
        assert prediction_service._classify_level(59.9) == "Normal"  # Justo antes del límite
        
        # Inundación
        assert prediction_service._classify_level(60.0) == "Inundación"  # Límite exacto
        assert prediction_service._classify_level(80.0) == "Inundación"
    
    def test_eliminate_outliers_iqr_improved(self, prediction_service, sample_data_with_outliers):
        """Probar eliminación de outliers con factor IQR conservador"""
        # Convertir a formato esperado
        formatted_data = []
        for doc in sample_data_with_outliers:
            formatted_data.append({
                'id': str(doc.id),
                'nivel_cm': float(doc.nivel_agua),
                'timestamp': datetime.fromisoformat(doc.timestamp)
            })
        
        niveles = [d['nivel_cm'] for d in formatted_data]
        clean_data = prediction_service._eliminar_outliers_iqr(formatted_data)
        
        # Verificar que se removieron outliers
        assert len(clean_data) < len(formatted_data)
        
        # Verificar que los valores están en rango razonable
        for d in clean_data:
            assert 0 <= d['nivel_cm'] <= 100
        
        # Verificar que los outliers extremos fueron removidos
        clean_levels = [d['nivel_cm'] for d in clean_data]
        assert max(clean_levels) < 100  # No debería haber valores > 100
        assert min(clean_levels) > -20  # No debería haber valores muy negativos
    
    def test_exponential_smoothing(self, prediction_service):
        """Probar suavizado exponencial"""
        # Crear datos con ruido
        data = []
        for i in range(20):
            nivel = 30.0 + np.sin(i * 0.5) * 5 + np.random.normal(0, 2)
            data.append({
                'id': f'test_{i}',
                'nivel_cm': nivel,
                'timestamp': datetime.now() - timedelta(minutes=i*5)
            })
        
        smoothed_data = prediction_service._aplicar_suavizado_exponencial(data, alpha=0.3)
        
        # Verificar que se mantuvieron todos los puntos
        assert len(smoothed_data) == len(data)
        
        # Verificar que el suavizado redujo la varianza
        original_variance = np.var([d['nivel_cm'] for d in data])
        smoothed_variance = np.var([d['nivel_cm'] for d in smoothed_data])
        assert smoothed_variance < original_variance
    
    def test_signal_analysis_window_moving(self, prediction_service, sample_data_ascending):
        """Probar análisis de señales con ventana móvil"""
        clean_data = prediction_service._preprocesar_datos_avanzado(sample_data_ascending, 180)
        signals = prediction_service._analizar_senales_ventana_movil(clean_data, 180)
        
        # Verificar estructura de respuesta
        assert 'pendiente_cm_por_h' in signals
        assert 'tendencia' in signals
        assert 'r_squared' in signals
        assert 'window_minutes' in signals
        assert 'data_points_window' in signals
        
        # Para datos ascendentes, la pendiente debería ser positiva
        assert signals['pendiente_cm_por_h'] > 0
        assert signals['tendencia'] == "sube"
        assert 0 <= signals['r_squared'] <= 1
    
    def test_signal_analysis_descending(self, prediction_service, sample_data_descending):
        """Probar análisis de señales con tendencia descendente"""
        clean_data = prediction_service._preprocesar_datos_avanzado(sample_data_descending, 180)
        signals = prediction_service._analizar_senales_ventana_movil(clean_data, 180)
        
        # Para datos descendentes, la pendiente debería ser negativa
        assert signals['pendiente_cm_por_h'] < 0
        assert signals['tendencia'] == "baja"
        assert 0 <= signals['r_squared'] <= 1
    
    def test_signal_analysis_stable(self, prediction_service, sample_data_stable):
        """Probar análisis de señales con tendencia estable"""
        clean_data = prediction_service._preprocesar_datos_avanzado(sample_data_stable, 180)
        signals = prediction_service._analizar_senales_ventana_movil(clean_data, 180)
        
        # Para datos estables, la pendiente debería ser pequeña
        assert abs(signals['pendiente_cm_por_h']) < 2.0
        assert signals['tendencia'] == "estable"
    
    def test_prediction_horizon_advanced(self, prediction_service, sample_data_ascending):
        """Probar generación de predicción avanzada para horizonte específico"""
        clean_data = prediction_service._preprocesar_datos_avanzado(sample_data_ascending, 180)
        signals = prediction_service._analizar_senales_ventana_movil(clean_data, 180)
        
        prediction = prediction_service._generar_prediccion_horizonte_avanzada(
            clean_data, signals, 120  # 2 horas
        )
        
        # Verificar estructura de respuesta
        assert 'horizon_min' in prediction
        assert 'nivel_cm' in prediction
        assert 'estado' in prediction
        assert 'confianza' in prediction
        
        assert prediction['horizon_min'] == 120
        assert prediction['nivel_cm'] >= 0  # No debe ser negativo
        assert 0.3 <= prediction['confianza'] <= 0.95  # Confianza limitada
        assert prediction['estado'] in ['Sequía', 'Normal', 'Inundación']
    
    def test_confidence_calculation(self, prediction_service, sample_data_ascending):
        """Probar cálculo de confianza basado en R² y cantidad de datos"""
        clean_data = prediction_service._preprocesar_datos_avanzado(sample_data_ascending, 180)
        signals = prediction_service._analizar_senales_ventana_movil(clean_data, 180)
        
        # Para datos con buena tendencia, la confianza debería ser alta
        prediction = prediction_service._generar_prediccion_horizonte_avanzada(
            clean_data, signals, 60
        )
        
        assert prediction['confianza'] >= 0.3
        assert prediction['confianza'] <= 0.95
        
        # Si hay muchos datos y buena correlación, confianza debería ser alta
        if signals['r_squared'] > 0.7 and signals['data_points_window'] > 20:
            assert prediction['confianza'] > 0.5
    
    def test_multi_horizon_predictions_improved(self, prediction_service, sample_data_ascending):
        """Probar predicciones multi-horizonte con mejoras"""
        horizons = [30, 60, 120, 180, 360]
        result = prediction_service.generar_predicciones_multi_horizonte(
            sample_data_ascending, horizons
        )
        
        # Verificar estructura de respuesta completa
        assert 'meta' in result
        assert 'current' in result
        assert 'predicciones' in result
        
        # Verificar metadata mejorada
        assert result['meta']['horizons'] == horizons
        assert 'generated_at' in result['meta']
        assert 'r2' in result['meta']
        assert 'points_used' in result['meta']
        assert 'sklearn_used' in result['meta']
        assert 0 <= result['meta']['r2'] <= 1
        
        # Verificar información actual
        assert 'nivel_cm' in result['current']
        assert 'estado' in result['current']
        assert 'tendencia' in result['current']
        assert 'pendiente_cm_por_h' in result['current']
        
        # Verificar predicciones
        assert len(result['predicciones']) == len(horizons)
        for pred in result['predicciones']:
            assert pred['horizon_min'] in horizons
            assert pred['nivel_cm'] >= 0
            assert pred['estado'] in ['Sequía', 'Normal', 'Inundación']
            assert 0.3 <= pred['confianza'] <= 0.95
    
    def test_noise_reduction_effectiveness(self, prediction_service, sample_data_noisy):
        """Probar efectividad de reducción de ruido"""
        # Procesar datos ruidosos
        clean_data = prediction_service._preprocesar_datos_avanzado(sample_data_noisy, 180)
        
        # Verificar que el preprocesamiento redujo el ruido
        original_levels = [doc.nivel_agua for doc in sample_data_noisy]
        clean_levels = [d['nivel_cm'] for d in clean_data]
        
        # El suavizado debería reducir la varianza
        original_variance = np.var(original_levels)
        clean_variance = np.var(clean_levels)
        
        # Nota: Esto podría fallar ocasionalmente debido a la naturaleza aleatoria
        # En un entorno de producción, se usarían datos determinísticos
        assert clean_variance <= original_variance * 1.2  # Permitir un pequeño margen
    
    def test_prediction_consistency(self, prediction_service, sample_data_ascending):
        """Probar consistencia de predicciones"""
        horizons = [30, 60, 120]
        
        # Generar predicciones múltiples veces
        results = []
        for _ in range(3):
            result = prediction_service.generar_predicciones_multi_horizonte(
                sample_data_ascending, horizons
            )
            results.append(result)
        
        # Las predicciones deberían ser consistentes (mismo R², misma tendencia)
        r2_values = [r['meta']['r2'] for r in results]
        tendencies = [r['current']['tendencia'] for r in results]
        
        # R² debería ser similar (dentro del 5%)
        for r2 in r2_values[1:]:
            assert abs(r2 - r2_values[0]) < 0.05
        
        # La tendencia debería ser la misma
        assert all(t == tendencies[0] for t in tendencies)
    
    def test_insufficient_data_handling(self, prediction_service):
        """Probar manejo de datos insuficientes"""
        # Crear datos insuficientes
        insufficient_data = []
        now = datetime.now()
        for i in range(5):  # Menos del mínimo requerido
            timestamp = now - timedelta(minutes=i*10)
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = 30.0
            doc.timestamp = timestamp.isoformat()
            insufficient_data.append(doc)
        
        horizons = [30, 60]
        result = prediction_service.generar_predicciones_multi_horizonte(
            insufficient_data, horizons
        )
        
        # Debe retornar respuesta de fallback
        assert 'meta' in result
        assert 'warning' in result['meta']
        assert result['meta']['points_used'] == 0
        assert result['meta']['r2'] == 0.0
        assert len(result['predicciones']) == len(horizons)
        
        # Todas las predicciones deben tener confianza mínima
        for pred in result['predicciones']:
            assert pred['confianza'] == 0.3
    
    def test_edge_cases(self, prediction_service):
        """Probar casos edge y manejo de errores"""
        # Datos vacíos
        result = prediction_service.generar_predicciones_multi_horizonte([])
        assert 'error' in result or 'warning' in result.get('meta', {})
        
        # Datos con valores extremos
        extreme_data = []
        now = datetime.now()
        for i in range(20):
            timestamp = now - timedelta(minutes=i*5)
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = -100 if i % 2 == 0 else 1000  # Valores extremos
            doc.timestamp = timestamp.isoformat()
            extreme_data.append(doc)
        
        result = prediction_service.generar_predicciones_multi_horizonte(extreme_data)
        # Debe manejar graciosamente los valores extremos
        assert 'error' in result or len(result.get('predicciones', [])) > 0


class TestPredictionServicePerformance:
    """Pruebas de rendimiento para el servicio de predicción"""
    
    def test_large_dataset_performance(self):
        """Probar rendimiento con dataset grande"""
        with patch('app.services.prediction_service.current_app') as mock_app:
            mock_app.config = {
                'DEFAULT_HORIZONS': [30, 60, 120, 180],
                'DROUGHT_MAX_CM': 20.0,
                'NORMAL_MAX_CM': 60.0,
                'REGRESSION_WINDOW_MIN': 180,
                'PREDICTION_MIN_DATA_POINTS': 10
            }
            mock_app.logger = Mock()
            
            service = PredictionService()
            
            # Crear dataset grande (1000 puntos)
            large_data = []
            now = datetime.now()
            for i in range(1000):
                timestamp = now - timedelta(minutes=i)
                nivel = 40.0 + np.sin(i * 0.01) * 10 + np.random.normal(0, 2)
                doc = Mock()
                doc.id = f"test_{i}"
                doc.nivel_agua = nivel
                doc.timestamp = timestamp.isoformat()
                large_data.append(doc)
            
            import time
            start_time = time.time()
            
            result = service.generar_predicciones_multi_horizonte(large_data)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Debe procesar 1000 puntos en menos de 1 segundo
            assert processing_time < 1.0
            assert 'predicciones' in result
            assert len(result['predicciones']) == 4
    
    def test_memory_usage(self):
        """Probar uso de memoria con dataset grande"""
        with patch('app.services.prediction_service.current_app') as mock_app:
            mock_app.config = {
                'DEFAULT_HORIZONS': [30, 60],
                'DROUGHT_MAX_CM': 20.0,
                'NORMAL_MAX_CM': 60.0,
                'REGRESSION_WINDOW_MIN': 120,
                'PREDICTION_MIN_DATA_POINTS': 10
            }
            mock_app.logger = Mock()
            
            service = PredictionService()
            
            # Crear múltiples datasets grandes
            datasets = []
            for _ in range(5):
                data = []
                now = datetime.now()
                for i in range(500):
                    timestamp = now - timedelta(minutes=i)
                    nivel = 30.0 + i * 0.1
                    doc = Mock()
                    doc.id = f"test_{i}"
                    doc.nivel_agua = nivel
                    doc.timestamp = timestamp.isoformat()
                    data.append(doc)
                datasets.append(data)
            
            # Procesar múltiples datasets
            results = []
            for data in datasets:
                result = service.generar_predicciones_multi_horizonte(data)
                results.append(result)
            
            # Todos deberían procesarse exitosamente
            assert all('predicciones' in r for r in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])