"""
Rutas para exportación de datos
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from http import HTTPStatus
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
from typing import Optional

from app.services.export_service import ExportService
from app.repositories.sensor_repository import SensorRepository
from app.repositories.user_repository import UserRepository
from app.repositories.alert_repository import AlertRepository
from app.utils.rate_limiter import api_rate_limit

# Crear blueprint
export_bp = Blueprint('export', __name__)

def get_export_service():
    """Obtener instancia del servicio de exportación"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB', 'sensor_database')
    
    client = MongoClient(mongo_uri)
    sensor_repository = SensorRepository(client, db_name)
    user_repository = UserRepository(client, db_name)
    
    # Alert repository es opcional
    alert_repository = None
    try:
        alert_repository = AlertRepository(client, db_name)
    except:
        current_app.logger.warning("AlertRepository no disponible")
    
    return ExportService(sensor_repository, user_repository, alert_repository)

@export_bp.route('/sensor-data', methods=['GET'])
@api_rate_limit()
def export_sensor_data():
    """
    Exportar datos de sensores
    
    Query Parameters:
        start_date: string (YYYY-MM-DD) - Fecha de inicio
        end_date: string (YYYY-MM-DD) - Fecha de fin
        format: string (csv, excel, pdf, json) - Formato de exportación
        filters: string (JSON) - Filtros adicionales
    
    Returns:
        200: Archivo de exportación
        400: Parámetros inválidos
        500: Error interno
    """
    try:
        # Validar parámetros requeridos
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        format_type = request.args.get('format', 'csv').lower()
        filters_str = request.args.get('filters')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'message': 'start_date y end_date son requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar formato
        if format_type not in ['csv', 'excel', 'pdf', 'json']:
            return jsonify({
                'success': False,
                'message': 'Formato no válido. Use: csv, excel, pdf, o json'
            }), HTTPStatus.BAD_REQUEST
        
        # Parsear fechas
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Agregar tiempo al final del día
            end_date = end_date.replace(hour=23, minute=59, second=59)
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': f'Formato de fecha inválido: {str(e)}'
            }), HTTPStatus.BAD_REQUEST
        
        # Parsear filtros si existen
        filters = None
        if filters_str:
            try:
                import json
                filters = json.loads(filters_str)
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'message': 'Filtros JSON inválidos'
                }), HTTPStatus.BAD_REQUEST
        
        # Exportar datos
        export_service = get_export_service()
        result = export_service.export_sensor_data(start_date, end_date, format_type, filters)
        
        if not result['success']:
            return jsonify(result), HTTPStatus.BAD_REQUEST
        
        # Crear buffer en memoria
        import io
        
        if format_type == 'csv' or format_type == 'json':
            # Para texto
            buffer = io.BytesIO(result['content'].encode('utf-8'))
        else:
            # Para binario
            buffer = io.BytesIO(result['content'])
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=result['filename'],
            mimetype=result['content_type']
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exportando datos de sensores: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno exportando datos'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@export_bp.route('/user-data', methods=['GET'])
@api_rate_limit()
def export_user_data():
    """
    Exportar datos de usuarios
    
    Query Parameters:
        format: string (csv, excel, pdf, json) - Formato de exportación
        filters: string (JSON) - Filtros adicionales
    
    Returns:
        200: Archivo de exportación
        400: Parámetros inválidos
        500: Error interno
    """
    try:
        # Validar parámetros
        format_type = request.args.get('format', 'csv').lower()
        filters_str = request.args.get('filters')
        
        # Validar formato
        if format_type not in ['csv', 'excel', 'pdf', 'json']:
            return jsonify({
                'success': False,
                'message': 'Formato no válido. Use: csv, excel, pdf, o json'
            }), HTTPStatus.BAD_REQUEST
        
        # Parsear filtros si existen
        filters = None
        if filters_str:
            try:
                import json
                filters = json.loads(filters_str)
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'message': 'Filtros JSON inválidos'
                }), HTTPStatus.BAD_REQUEST
        
        # Exportar datos
        export_service = get_export_service()
        result = export_service.export_user_data(format_type, filters)
        
        if not result['success']:
            return jsonify(result), HTTPStatus.BAD_REQUEST
        
        # Crear buffer en memoria
        import io
        
        if format_type == 'csv' or format_type == 'json':
            # Para texto
            buffer = io.BytesIO(result['content'].encode('utf-8'))
        else:
            # Para binario
            buffer = io.BytesIO(result['content'])
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=result['filename'],
            mimetype=result['content_type']
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exportando datos de usuarios: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno exportando datos'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@export_bp.route('/alert-data', methods=['GET'])
@api_rate_limit()
def export_alert_data():
    """
    Exportar datos de alertas
    
    Query Parameters:
        start_date: string (YYYY-MM-DD) - Fecha de inicio
        end_date: string (YYYY-MM-DD) - Fecha de fin
        format: string (csv, excel, pdf, json) - Formato de exportación
        filters: string (JSON) - Filtros adicionales
    
    Returns:
        200: Archivo de exportación
        400: Parámetros inválidos
        500: Error interno
    """
    try:
        # Validar parámetros requeridos
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        format_type = request.args.get('format', 'csv').lower()
        filters_str = request.args.get('filters')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'message': 'start_date y end_date son requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar formato
        if format_type not in ['csv', 'excel', 'pdf', 'json']:
            return jsonify({
                'success': False,
                'message': 'Formato no válido. Use: csv, excel, pdf, o json'
            }), HTTPStatus.BAD_REQUEST
        
        # Parsear fechas
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': f'Formato de fecha inválido: {str(e)}'
            }), HTTPStatus.BAD_REQUEST
        
        # Parsear filtros si existen
        filters = None
        if filters_str:
            try:
                import json
                filters = json.loads(filters_str)
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'message': 'Filtros JSON inválidos'
                }), HTTPStatus.BAD_REQUEST
        
        # Exportar datos
        export_service = get_export_service()
        result = export_service.export_alert_data(start_date, end_date, format_type, filters)
        
        if not result['success']:
            return jsonify(result), HTTPStatus.BAD_REQUEST
        
        # Crear buffer en memoria
        import io
        
        if format_type == 'csv' or format_type == 'json':
            # Para texto
            buffer = io.BytesIO(result['content'].encode('utf-8'))
        else:
            # Para binario
            buffer = io.BytesIO(result['content'])
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=result['filename'],
            mimetype=result['content_type']
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exportando datos de alertas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno exportando datos'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@export_bp.route('/system-report', methods=['GET'])
@api_rate_limit()
def export_system_report():
    """
    Exportar reporte completo del sistema
    
    Query Parameters:
        start_date: string (YYYY-MM-DD) - Fecha de inicio
        end_date: string (YYYY-MM-DD) - Fecha de fin
        format: string (pdf, excel) - Formato de exportación
    
    Returns:
        200: Archivo de reporte
        400: Parámetros inválidos
        500: Error interno
    """
    try:
        # Validar parámetros requeridos
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        format_type = request.args.get('format', 'pdf').lower()
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'message': 'start_date y end_date son requeridos'
            }), HTTPStatus.BAD_REQUEST
        
        # Validar formato
        if format_type not in ['pdf', 'excel']:
            return jsonify({
                'success': False,
                'message': 'Formato no válido. Use: pdf o excel'
            }), HTTPStatus.BAD_REQUEST
        
        # Parsear fechas
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': f'Formato de fecha inválido: {str(e)}'
            }), HTTPStatus.BAD_REQUEST
        
        # Generar reporte
        export_service = get_export_service()
        result = export_service.export_system_report(start_date, end_date, format_type)
        
        if not result['success']:
            return jsonify(result), HTTPStatus.BAD_REQUEST
        
        # Crear buffer en memoria
        import io
        buffer = io.BytesIO(result['content'])
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=result['filename'],
            mimetype=result['content_type']
        )
        
    except Exception as e:
        current_app.logger.error(f"Error generando reporte del sistema: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno generando reporte'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@export_bp.route('/formats', methods=['GET'])
def get_export_formats():
    """
    Obtener formatos de exportación disponibles
    
    Returns:
        200: Lista de formatos disponibles
    """
    try:
        formats = {
            'sensor_data': ['csv', 'excel', 'pdf', 'json'],
            'user_data': ['csv', 'excel', 'pdf', 'json'],
            'alert_data': ['csv', 'excel', 'pdf', 'json'],
            'system_report': ['pdf', 'excel']
        }
        
        return jsonify({
            'success': True,
            'formats': formats
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo formatos: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
