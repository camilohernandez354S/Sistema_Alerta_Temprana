#!/usr/bin/env python3
"""
Script de inicialización para configurar datos geoespaciales de prueba
Crea sensores con ubicaciones y genera mediciones de ejemplo
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.geospatial_service import geospatial_service

def setup_test_sensors():
    """
    Configurar sensores de prueba con ubicaciones reales
    """
    print("🔧 Configurando sensores de prueba...")
    
    # Sensores de prueba con ubicaciones reales en Buenos Aires
    test_sensors = [
        {
            'sensor_id': 'sensor_001',
            'lat': -34.6037,
            'lng': -58.3816,
            'nombre': 'Sensor Centro',
            'descripcion': 'Sensor principal en el centro de Buenos Aires'
        },
        {
            'sensor_id': 'sensor_002', 
            'lat': -34.6118,
            'lng': -58.3960,
            'nombre': 'Sensor Puerto Madero',
            'descripcion': 'Sensor en Puerto Madero, zona costera'
        },
        {
            'sensor_id': 'sensor_003',
            'lat': -34.5875,
            'lng': -58.3974,
            'nombre': 'Sensor La Boca',
            'descripcion': 'Sensor en La Boca, zona de riesgo de inundación'
        },
        {
            'sensor_id': 'sensor_004',
            'lat': -34.6092,
            'lng': -58.3731,
            'nombre': 'Sensor Recoleta',
            'descripcion': 'Sensor en Recoleta, zona residencial'
        },
        {
            'sensor_id': 'sensor_005',
            'lat': -34.6158,
            'lng': -58.4333,
            'nombre': 'Sensor Palermo',
            'descripcion': 'Sensor en Palermo, zona de parques'
        }
    ]
    
    created_sensors = []
    for sensor in test_sensors:
        result = geospatial_service.create_sensor_with_location(
            sensor_id=sensor['sensor_id'],
            lat=sensor['lat'],
            lng=sensor['lng'],
            nombre=sensor['nombre'],
            descripcion=sensor['descripcion']
        )
        
        if result['success']:
            created_sensors.append(sensor)
            print(f"✅ {sensor['nombre']} configurado en {sensor['lat']}, {sensor['lng']}")
        else:
            print(f"❌ Error configurando {sensor['nombre']}: {result['error']}")
    
    return created_sensors

def generate_test_measurements(sensors, days_back=7):
    """
    Generar mediciones de prueba para los sensores
    """
    print(f"📊 Generando mediciones de prueba (últimos {days_back} días)...")
    
    # Estados posibles con sus rangos de nivel
    states_config = {
        'normal': {'min': 20, 'max': 35, 'probability': 0.6},
        'sequia': {'min': 40, 'max': 60, 'probability': 0.2},
        'inundacion': {'min': 5, 'max': 15, 'probability': 0.2}
    }
    
    measurements_created = 0
    start_date = datetime.utcnow() - timedelta(days=days_back)
    
    for sensor in sensors:
        print(f"  📍 Generando mediciones para {sensor['nombre']}...")
        
        # Generar mediciones cada 30 minutos
        current_date = start_date
        while current_date <= datetime.utcnow():
            # Determinar estado basado en probabilidades
            rand = random.random()
            cumulative = 0
            selected_state = 'normal'
            
            for state, config in states_config.items():
                cumulative += config['probability']
                if rand <= cumulative:
                    selected_state = state
                    break
            
            # Generar nivel basado en el estado
            state_config = states_config[selected_state]
            nivel = random.uniform(state_config['min'], state_config['max'])
            
            # Agregar variación temporal (simular patrones)
            if current_date.hour >= 6 and current_date.hour <= 18:  # Día
                nivel += random.uniform(-2, 2)
            else:  # Noche
                nivel += random.uniform(-1, 1)
            
            # Asegurar que el nivel esté en el rango correcto
            nivel = max(0, min(100, nivel))
            
            # Crear medición
            result = geospatial_service.save_measurement_with_location(
                sensor_id=sensor['sensor_id'],
                nivel=round(nivel, 1),
                estado=selected_state,
                lat=sensor['lat'],
                lng=sensor['lng']
            )
            
            if result['success']:
                measurements_created += 1
            
            # Avanzar 30 minutos
            current_date += timedelta(minutes=30)
    
    print(f"✅ {measurements_created} mediciones generadas")
    return measurements_created

def test_geospatial_queries():
    """
    Probar las consultas geoespaciales
    """
    print("🔍 Probando consultas geoespaciales...")
    
    # Centro de Buenos Aires
    test_center = {'lat': -34.6037, 'lng': -58.3816}
    
    # Probar diferentes radios
    test_radii = [1000, 5000, 10000]  # 1km, 5km, 10km
    
    for radius in test_radii:
        result = geospatial_service.get_alerts_in_radius(
            lat=test_center['lat'],
            lng=test_center['lng'],
            radius_meters=radius
        )
        
        if result['success']:
            print(f"  📍 Radio {radius}m: {result['total']} alertas encontradas")
        else:
            print(f"  ❌ Error en radio {radius}m: {result['error']}")

def main():
    """
    Función principal de inicialización
    """
    print("🚀 Inicializando datos geoespaciales del Sistema de Alerta Temprana")
    print("=" * 70)
    
    try:
        # 1. Configurar sensores
        sensors = setup_test_sensors()
        
        if not sensors:
            print("❌ No se pudieron configurar sensores. Abortando.")
            return
        
        # 2. Generar mediciones de prueba
        measurements = generate_test_measurements(sensors)
        
        # 3. Probar consultas geoespaciales
        test_geospatial_queries()
        
        print("\n" + "=" * 70)
        print("✅ Inicialización completada exitosamente!")
        print(f"📊 Sensores configurados: {len(sensors)}")
        print(f"📈 Mediciones generadas: {measurements}")
        print("\n🌐 Endpoints disponibles:")
        print("  - GET /api/alertas?lat={lat}&lng={lng}&radio={metros}")
        print("  - GET /api/sensores")
        print("  - POST /api/sensores")
        print("  - POST /api/mediciones")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cerrar conexión
        geospatial_service.close_connection()

if __name__ == "__main__":
    main()
