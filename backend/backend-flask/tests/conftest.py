"""
Configuración para pytest
"""
import pytest
import os
from app import create_app
from app.factory import ServiceFactory

@pytest.fixture
def app():
    """Fixture de aplicación Flask para testing"""
    # Configurar variables de entorno para testing
    os.environ['FLASK_ENV'] = 'testing'
    
    app = create_app('testing')
    
    # Configurar contexto de aplicación
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Fixture de cliente Flask para testing"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture de runner CLI para testing"""
    return app.test_cli_runner()

@pytest.fixture
def service_factory(app):
    """Fixture de factory de servicios para testing"""
    with app.app_context():
        factory = ServiceFactory()
        yield factory
        factory.cleanup()

class MockSensorRepository:
    """Mock del repository para testing"""
    
    def __init__(self):
        self.data = []
    
    def insert_one(self, document):
        self.data.append(document)
        return "mock_id"
    
    def find_all(self, limit=None):
        result = self.data[-limit:] if limit else self.data
        return result
    
    def find_latest(self):
        return self.data[-1] if self.data else None
    
    def health_check(self):
        return True
