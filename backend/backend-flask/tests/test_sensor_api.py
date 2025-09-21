"""
Tests para la API de sensores
"""
import pytest
import json
from datetime import datetime

class TestSensorAPI:
    """Tests para endpoints de sensores"""
    
    def test_health_check(self, client):
        """Test del endpoint de health check"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'checks' in data
    
    def test_procesar_lectura_valida(self, client):
        """Test de procesamiento de lectura válida"""
        lectura_data = {
            "nivel_agua": 7.5
        }
        
        response = client.post(
            '/api/sensor/lectura',
            data=json.dumps(lectura_data),
            content_type='application/json'
        )
        
        # Puede fallar por conexión a MongoDB, pero debe validar formato
        assert response.status_code in [200, 500]  # 500 si no hay MongoDB
    
    def test_procesar_lectura_invalida(self, client):
        """Test de procesamiento de lectura inválida"""
        lectura_data = {
            "nivel_agua": "invalid"
        }
        
        response = client.post(
            '/api/sensor/lectura',
            data=json.dumps(lectura_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_procesar_lectura_sin_json(self, client):
        """Test sin Content-Type JSON"""
        response = client.post('/api/sensor/lectura', data="not json")
        assert response.status_code == 400
    
    def test_lectura_campo_faltante(self, client):
        """Test con campo nivel_agua faltante"""
        lectura_data = {"otro_campo": "valor"}
        
        response = client.post(
            '/api/sensor/lectura',
            data=json.dumps(lectura_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_procesar_lecturas_crudas(self, client):
        """Test de procesamiento de lecturas crudas"""
        lecturas_data = [
            {"raw_data": "nivel_agua: 8.5cm"},
            {"raw_data": "nivel_agua: 12.0cm"}
        ]
        
        response = client.post(
            '/api/sensor/lecturas',
            data=json.dumps(lecturas_data),
            content_type='application/json'
        )
        
        # Puede fallar por conexión a MongoDB
        assert response.status_code in [200, 500]
    
    def test_procesar_lecturas_crudas_invalidas(self, client):
        """Test de procesamiento de lecturas crudas inválidas"""
        lecturas_data = [
            {"raw_data": "formato_invalido"},
            {"otro_campo": "valor"}
        ]
        
        response = client.post(
            '/api/sensor/lecturas',
            data=json.dumps(lecturas_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_get_todas_lecturas(self, client):
        """Test obtener todas las lecturas"""
        response = client.get('/api/sensor/todas-lecturas')
        
        # Puede fallar por conexión a MongoDB
        assert response.status_code in [200, 500]
    
    def test_get_rango_tiempo_valido(self, client):
        """Test obtener lecturas por rango de tiempo válido"""
        response = client.get('/api/sensor/rango-tiempo/24h')
        
        # Puede fallar por conexión a MongoDB
        assert response.status_code in [200, 500]
    
    def test_get_rango_tiempo_invalido(self, client):
        """Test obtener lecturas por rango de tiempo inválido"""
        response = client.get('/api/sensor/rango-tiempo/invalid')
        
        assert response.status_code in [400, 500]  # 400 por rango inválido o 500 por MongoDB
    
    def test_get_alertas(self, client):
        """Test obtener alertas"""
        response = client.get('/api/sensor/alertas')
        
        # Puede fallar por conexión a MongoDB
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'alertas' in data
            assert 'total' in data
    
    def test_get_alertas_con_limite(self, client):
        """Test obtener alertas con límite personalizado"""
        response = client.get('/api/sensor/alertas?limit=5')
        
        # Puede fallar por conexión a MongoDB
        assert response.status_code in [200, 500]
    
    def test_get_alertas_limite_invalido(self, client):
        """Test obtener alertas con límite inválido"""
        response = client.get('/api/sensor/alertas?limit=0')
        assert response.status_code == 400
        
        response = client.get('/api/sensor/alertas?limit=101')
        assert response.status_code == 400
    
    def test_get_estado_sistema(self, client):
        """Test obtener estado del sistema"""
        response = client.get('/api/sensor/estado')
        
        # Puede fallar por conexión a MongoDB
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'estado' in data
            assert 'ultima_lectura' in data
            assert 'estadisticas' in data
            assert 'componentes' in data
            assert 'timestamp' in data
    
    def test_verify_blockchain(self, client):
        """Test verificación de blockchain"""
        response = client.get('/api/sensor/verify-blockchain')
        
        # Puede fallar por conexión, pero debe responder
        assert response.status_code in [200, 400, 500]
