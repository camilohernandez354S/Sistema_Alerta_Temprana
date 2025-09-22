"""
Pruebas para el servicio de predicción
"""
import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.services.prediction_service import PredictionService
from app.models.sensor_model import SensorDocumentObtenido


class TestPredictionService:
    """Pruebas para PredictionService"""
    
    @pytest.fixture
    def prediction_service(self):
        """Fixture para el servicio de predicción"""
        with patch('app.services.prediction_service.current_app') as mock_app:
            mock_app.config = {
                'DEFAULT_HORIZONS': [30, 60, 180],
                'DROUGHT_MAX_CM': 20.0,
                'NORMAL_MAX_CM': 60.0,
                'REGRESSION_WINDOW_MIN': 120,
                'PREDICTION_MIN_DATA_POINTS': 10
            }
            mock_app.logger = Mock()
            service = PredictionService()
            return service
    
    @pytest.fixture
    def sample_data_ascending(self):
        """Datos de prueba con tendencia ascendente"""
        now = datetime.now()
        data = []
        for i in range(20):
            timestamp = now - timedelta(minutes=i*5)
            nivel = 10.0 + (i * 0.5)  # Tendencia ascendente
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    @pytest.fixture
    def sample_data_descending(self):
        """Datos de prueba con tendencia descendente"""
        now = datetime.now()
        data = []
        for i in range(20):
            timestamp = now - timedelta(minutes=i*5)
            nivel = 50.0 - (i * 0.5)  # Tendencia descendente
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    @pytest.fixture
    def sample_data_with_outliers(self):
        """Datos de prueba con outliers"""
        now = datetime.now()
        data = []
        for i in range(20):
            timestamp = now - timedelta(minutes=i*5)
            nivel = 30.0 + np.sin(i * 0.1) * 5  # Datos normales
            # Agregar outliers en posiciones específicas
            if i in [5, 10, 15]:
                nivel += 50  # Outlier grande
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        return data
    
    def test_classify_level_normal(self, prediction_service):
        """Probar clasificación de nivel normal"""
        assert prediction_service._classify_level(30.0) == "Normal"
        assert prediction_service._classify_level(45.0) == "Normal"
    
    def test_classify_level_drought(self, prediction_service):
        """Probar clasificación de nivel de sequía"""
        assert prediction_service._classify_level(15.0) == "Sequía"
        assert prediction_service._classify_level(5.0) == "Sequía"
    
    def test_classify_level_flood(self, prediction_service):
        """Probar clasificación de nivel de inundación"""
        assert prediction_service._classify_level(65.0) == "Inundación"
        assert prediction_service._classify_level(80.0) == "Inundación"
    
    def test_preprocess_data_validation(self, prediction_service, sample_data_ascending):
        """Probar validación de esquema en preprocesamiento"""
        # Datos válidos
        clean_data = prediction_service._preprocesar_datos(sample_data_ascending)
        assert len(clean_data) > 0
        assert all('nivel_cm' in d for d in clean_data)
        assert all('timestamp' in d for d in clean_data)
    
    def test_remove_outliers_iqr(self, prediction_service, sample_data_with_outliers):
        """Probar remoción de outliers con IQR"""
        # Convertir a formato esperado
        formatted_data = []
        for doc in sample_data_with_outliers:
            formatted_data.append({
                'id': str(doc.id),
                'nivel_cm': float(doc.nivel_agua),
                'timestamp': datetime.fromisoformat(doc.timestamp)
            })
        
        niveles = [d['nivel_cm'] for d in formatted_data]
        clean_data = prediction_service._remover_outliers_iqr(formatted_data, niveles)
        
        # Verificar que se removieron outliers
        assert len(clean_data) < len(formatted_data)
        # Verificar que los valores están en rango razonable
        for d in clean_data:
            assert 0 <= d['nivel_cm'] <= 100
    
    def test_signal_analysis_ascending_trend(self, prediction_service, sample_data_ascending):
        """Probar análisis de señales con tendencia ascendente"""
        clean_data = prediction_service._preprocesar_datos(sample_data_ascending)
        signals = prediction_service._analizar_senales(clean_data)
        
        assert signals['tendencia'] == "sube"
        assert signals['pendiente_cm_por_h'] > 0
        assert 'r_squared' in signals
        assert signals['window_minutes'] > 0
    
    def test_signal_analysis_descending_trend(self, prediction_service, sample_data_descending):
        """Probar análisis de señales con tendencia descendente"""
        clean_data = prediction_service._preprocesar_datos(sample_data_descending)
        signals = prediction_service._analizar_senales(clean_data)
        
        assert signals['tendencia'] == "baja"
        assert signals['pendiente_cm_por_h'] < 0
        assert 'r_squared' in signals
        assert signals['window_minutes'] > 0
    
    def test_prediction_horizon_generation(self, prediction_service, sample_data_ascending):
        """Probar generación de predicción para horizonte específico"""
        clean_data = prediction_service._preprocesar_datos(sample_data_ascending)
        signals = prediction_service._analizar_senales(clean_data)
        
        prediction = prediction_service._generar_prediccion_horizonte(
            clean_data, signals, 60  # 60 minutos
        )
        
        assert 'horizon_min' in prediction
        assert 'nivel_cm' in prediction
        assert 'estado' in prediction
        assert 'confianza' in prediction
        assert prediction['horizon_min'] == 60
        assert prediction['nivel_cm'] >= 0  # No debe ser negativo
        assert prediction['confianza'] >= 0 and prediction['confianza'] <= 1
    
    def test_multi_horizon_predictions(self, prediction_service, sample_data_ascending):
        """Probar predicciones multi-horizonte"""
        horizons = [30, 60, 180]
        result = prediction_service.generar_predicciones_multi_horizonte(
            sample_data_ascending, horizons
        )
        
        # Verificar estructura de respuesta
        assert 'meta' in result
        assert 'current' in result
        assert 'predicciones' in result
        
        # Verificar metadata
        assert result['meta']['horizons'] == horizons
        assert 'generated_at' in result['meta']
        assert result['meta']['data_points_used'] > 0
        
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
            assert 0 <= pred['confianza'] <= 1
    
    def test_insufficient_data_fallback(self, prediction_service):
        """Probar fallback cuando no hay suficientes datos"""
        # Crear datos insuficientes (menos de 10 puntos)
        insufficient_data = []
        now = datetime.now()
        for i in range(5):
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
        assert result['meta']['data_points_used'] == 0
        assert len(result['predicciones']) == len(horizons)
        
        # Todas las predicciones deben tener confianza baja
        for pred in result['predicciones']:
            assert pred['confianza'] == 0.1
    
    def test_error_handling(self, prediction_service):
        """Probar manejo de errores"""
        # Datos corruptos
        corrupt_data = []
        doc = Mock()
        doc.id = "corrupt"
        doc.nivel_agua = "not_a_number"  # Valor inválido
        doc.timestamp = "invalid_timestamp"
        corrupt_data.append(doc)
        
        result = prediction_service.generar_predicciones_multi_horizonte(corrupt_data)
        
        # Debe retornar respuesta de fallback o error
        assert 'error' in result or 'warning' in result.get('meta', {})
    
    def test_interpolation_gap_filling(self, prediction_service):
        """Probar interpolación de huecos pequeños"""
        # Crear datos con hueco
        now = datetime.now()
        data = []
        
        # Punto inicial
        doc1 = Mock()
        doc1.id = "1"
        doc1.nivel_agua = 30.0
        doc1.timestamp = now.isoformat()
        data.append(doc1)
        
        # Punto final (60 minutos después)
        doc2 = Mock()
        doc2.id = "2"
        doc2.nivel_agua = 35.0
        doc2.timestamp = (now + timedelta(minutes=60)).isoformat()
        data.append(doc2)
        
        clean_data = prediction_service._preprocesar_datos(data)
        
        # Debe haber interpolado puntos intermedios
        assert len(clean_data) > 2
    
    def test_moving_average_smoothing(self, prediction_service):
        """Probar suavizado con media móvil"""
        # Crear datos con ruido
        now = datetime.now()
        data = []
        for i in range(10):
            timestamp = now - timedelta(minutes=i*5)
            # Datos con ruido
            nivel = 30.0 + np.random.normal(0, 2)
            doc = Mock()
            doc.id = f"test_{i}"
            doc.nivel_agua = nivel
            doc.timestamp = timestamp.isoformat()
            data.append(doc)
        
        clean_data = prediction_service._preprocesar_datos(data)
        
        # Verificar que se mantuvieron todos los puntos
        assert len(clean_data) == len(data)
        
        # Verificar que los valores están en rango razonable
        for d in clean_data:
            assert isinstance(d['nivel_cm'], (int, float))
            assert d['nivel_cm'] >= 0


class TestPredictionServiceIntegration:
    """Pruebas de integración para el servicio de predicción"""
    
    def test_end_to_end_prediction_workflow(self):
        """Probar flujo completo de predicción"""
        with patch('app.services.prediction_service.current_app') as mock_app:
            mock_app.config = {
                'DEFAULT_HORIZONS': [30, 60, 180],
                'DROUGHT_MAX_CM': 20.0,
                'NORMAL_MAX_CM': 60.0,
                'REGRESSION_WINDOW_MIN': 120,
                'PREDICTION_MIN_DATA_POINTS': 10
            }
            mock_app.logger = Mock()
            
            service = PredictionService()
            
            # Crear datos realistas
            now = datetime.now()
            data = []
            for i in range(50):  # Suficientes datos
                timestamp = now - timedelta(minutes=i*3)
                # Tendencia ligeramente ascendente con variación
                nivel = 40.0 + (i * 0.1) + np.sin(i * 0.2) * 3
                doc = Mock()
                doc.id = f"test_{i}"
                doc.nivel_agua = nivel
                doc.timestamp = timestamp.isoformat()
                data.append(doc)
            
            # Ejecutar predicción completa
            result = service.generar_predicciones_multi_horizonte(data)
            
            # Verificar resultado completo
            assert 'meta' in result
            assert 'current' in result
            assert 'predicciones' in result
            assert len(result['predicciones']) == 3
            
            # Verificar que la tendencia es detectada correctamente
            assert result['current']['tendencia'] in ['sube', 'baja', 'estable']
            
            # Verificar que las predicciones son consistentes
            for pred in result['predicciones']:
                assert pred['nivel_cm'] >= 0
                assert pred['confianza'] > 0
                assert pred['estado'] in ['Sequía', 'Normal', 'Inundación']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
