"""
Rutas de salud y diagnóstico del sistema
"""
from flask import Blueprint, jsonify, current_app
from pymongo import MongoClient
from datetime import datetime
import os

# Crear blueprint para health checks
health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint básico de salud del sistema
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Sistema de Alerta Temprana API'
    })

@health_bp.route('/api/health/database', methods=['GET'])
def database_health_check():
    """
    Verificar conexión y estado de la base de datos MongoDB
    """
    try:
        # Obtener configuración de MongoDB
        mongo_uri = current_app.config.get('MONGO_URI')
        db_name = current_app.config.get('MONGO_DB')
        
        # Crear conexión temporal
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Verificar conexión
        ping_result = client.admin.command('ping')
        
        # Obtener información de la base de datos
        db_stats = db.command("dbStats")
        collections = db.list_collection_names()
        
        # Obtener conteo de documentos en cada colección
        collection_counts = {}
        for collection_name in collections:
            try:
                count = db[collection_name].count_documents({})
                collection_counts[collection_name] = count
            except Exception as e:
                collection_counts[collection_name] = f"Error: {str(e)}"
        
        # Cerrar conexión
        client.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'connected': True,
                'name': db_name,
                'uri': mongo_uri.replace(mongo_uri.split('@')[0].split('://')[1], '***') if '@' in mongo_uri else mongo_uri,
                'collections': collections,
                'collection_counts': collection_counts,
                'size_bytes': db_stats.get('dataSize', 0),
                'indexes': db_stats.get('indexes', 0)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'connected': False,
                'error': str(e),
                'mongo_uri': current_app.config.get('MONGO_URI', 'Not configured'),
                'db_name': current_app.config.get('MONGO_DB', 'Not configured')
            }
        }), 500

@health_bp.route('/api/health/config', methods=['GET'])
def config_health_check():
    """
    Verificar configuración del sistema (sin exponer información sensible)
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'config': {
            'flask_env': current_app.config.get('FLASK_ENV', 'Not set'),
            'debug': current_app.config.get('DEBUG', False),
            'mongo_db': current_app.config.get('MONGO_DB', 'Not set'),
            'cors_configured': bool(current_app.config.get('CORS_ORIGINS', False)),
            'secret_key_configured': bool(current_app.config.get('SECRET_KEY', False))
        }
    })

@health_bp.route('/api/health/test-insert', methods=['POST'])
def test_database_insert():
    """
    Probar inserción de datos en la base de datos
    """
    try:
        # Obtener configuración de MongoDB
        mongo_uri = current_app.config.get('MONGO_URI')
        db_name = current_app.config.get('MONGO_DB')
        
        # Crear conexión temporal
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Crear documento de prueba
        test_doc = {
            'timestamp': datetime.utcnow(),
            'tipo': 'test',
            'mensaje': 'Prueba de inserción desde health check',
            'nivel_agua': 25.5,
            'location': {
                'type': 'Point',
                'coordinates': [-74.0, 4.6]  # Bogotá, Colombia
            }
        }
        
        # Insertar en colección de mediciones
        result = db['mediciones'].insert_one(test_doc)
        
        # Verificar que se insertó correctamente
        inserted_doc = db['mediciones'].find_one({'_id': result.inserted_id})
        
        # Eliminar el documento de prueba
        db['mediciones'].delete_one({'_id': result.inserted_id})
        
        # Cerrar conexión
        client.close()
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'test_result': {
                'inserted_id': str(result.inserted_id),
                'document_verified': bool(inserted_doc),
                'test_document_removed': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500
