# 🗺️ Módulo de Alertas Georreferenciadas - Documentación Completa

## Resumen

Módulo especializado para el Sistema de Alerta Temprana que implementa funcionalidades geoespaciales, permitiendo consultar alertas por proximidad geográfica con área circular configurable.

## 📋 Características Implementadas

### ✅ Backend (Flask + MongoDB)

#### Modelo de Datos Geoespaciales
- **Colección `mediciones`**: Extendida con campo `location` tipo GeoJSON Point
- **Colección `sensores`**: Nueva colección para almacenar ubicaciones de sensores
- **Índices 2dsphere**: Optimización automática para consultas geoespaciales

#### Endpoints REST
- `GET /api/alertas?lat={lat}&lng={lng}&radio={metros}` - Consultar alertas por proximidad
- `GET /api/sensores` - Obtener todos los sensores registrados
- `POST /api/sensores` - Crear/actualizar sensor con ubicación
- `POST /api/mediciones` - Guardar medición con datos geoespaciales

#### Servicios Especializados
- **GeospatialService**: Manejo de operaciones geoespaciales
- **Consultas $near**: Búsqueda por proximidad con radio configurable
- **Cálculo de distancias**: Fórmula de Haversine para distancias precisas

### ✅ Frontend (Vue + Leaflet)

#### Componente de Mapa Interactivo
- **Leaflet Integration**: Mapa interactivo con OpenStreetMap
- **Selección de Área Circular**: Radio configurable (1km, 2km, 5km, 10km, 20km)
- **Geolocalización**: Obtención automática de ubicación del usuario
- **Marcadores Dinámicos**: Visualización de alertas con colores por estado
- **Actualización Automática**: Refresco cada 30 segundos sin mostrar "cargando"

#### Funcionalidades de Usuario
- **Clic en Mapa**: Buscar alertas en ubicación seleccionada
- **Botón "Mi Ubicación"**: Centrar mapa en ubicación actual
- **Lista de Alertas**: Panel con detalles de alertas encontradas
- **Información de Distancia**: Cálculo y visualización de distancias

## 🏗️ Arquitectura del Módulo

```
Frontend (Vue + Leaflet)
    ↓ HTTP Requests
Backend (Flask + GeoJSON)
    ↓ MongoDB Queries
MongoDB (2dsphere Indexes)
    ↓ GeoJSON Documents
Sensores + Mediciones
```

## 📊 Esquema de Base de Datos

### Colección: `mediciones` (Extendida)

```javascript
{
  "_id": ObjectId,
  "sensor_id": "string",
  "location": {
    "type": "Point",
    "coordinates": [lng, lat]  // [longitud, latitud]
  },
  "nivel": "float",
  "estado": "string",  // sequia | normal | inundacion
  "timestamp": ISODate
}
```

### Colección: `sensores` (Nueva)

```javascript
{
  "_id": ObjectId,
  "sensor_id": "string",
  "location": {
    "type": "Point", 
    "coordinates": [lng, lat]
  },
  "nombre": "string",
  "descripcion": "string",
  "activo": boolean,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

## 🔧 Instalación y Configuración

### 1. Backend

```bash
# Instalar dependencias (ya incluidas en requirements.txt)
pip install pymongo

# Ejecutar script de inicialización
cd backend/backend-flask
python setup_geospatial_data.py
```

### 2. Frontend

```bash
# Instalar dependencias de Leaflet
cd frontend
npm install leaflet vue3-leaflet

# Iniciar servidor de desarrollo
npm run dev
```

## 📡 API Endpoints

### GET /api/alertas

Obtener alertas dentro de un radio circular específico.

**Parámetros:**
- `lat` (float, requerido): Latitud del punto central
- `lng` (float, requerido): Longitud del punto central  
- `radio` (int, opcional): Radio en metros (default: 5000)

**Ejemplo:**
```bash
curl "http://localhost:5000/api/alertas?lat=-34.6037&lng=-58.3816&radio=5000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "alerts": [
    {
      "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
      "sensor_id": "sensor_001",
      "location": {
        "type": "Point",
        "coordinates": [-58.3816, -34.6037]
      },
      "nivel": 25.5,
      "estado": "normal",
      "timestamp": "2024-01-15T10:30:00Z",
      "sensor_nombre": "Sensor Centro",
      "distancia_km": 0.0
    }
  ],
  "total": 1,
  "center": {"lat": -34.6037, "lng": -58.3816},
  "radius_meters": 5000
}
```

### POST /api/sensores

Crear o actualizar un sensor con ubicación geográfica.

**Body:**
```json
{
  "sensor_id": "sensor_001",
  "lat": -34.6037,
  "lng": -58.3816,
  "nombre": "Sensor Centro",
  "descripcion": "Sensor principal en el centro"
}
```

### POST /api/mediciones

Guardar medición con datos geoespaciales.

**Body:**
```json
{
  "sensor_id": "sensor_001",
  "nivel": 25.5,
  "estado": "normal",
  "lat": -34.6037,
  "lng": -58.3816
}
```

## 🗺️ Consultas Geoespaciales en MongoDB

### Consulta Básica con $near

```javascript
db.mediciones.find({
  "location": {
    "$near": {
      "$geometry": {
        "type": "Point",
        "coordinates": [-58.3816, -34.6037]
      },
      "$maxDistance": 5000  // 5km en metros
    }
  },
  "estado": {"$in": ["sequia", "inundacion"]}
})
```

### Crear Índice 2dsphere

```javascript
db.mediciones.createIndex({"location": "2dsphere"})
db.sensores.createIndex({"location": "2dsphere"})
```

## 🎨 Componentes Frontend

### GeospatialMap.vue

Componente principal del mapa con las siguientes características:

- **Props:**
  - `initialLat`: Latitud inicial del mapa
  - `initialLng`: Longitud inicial del mapa
  - `initialZoom`: Nivel de zoom inicial

- **Funcionalidades:**
  - Mapa interactivo con Leaflet
  - Selección de radio de búsqueda
  - Geolocalización del usuario
  - Marcadores de alertas con colores por estado
  - Círculo de radio visual
  - Lista de alertas encontradas
  - Actualización automática cada 30 segundos

### geospatialService.js

Servicio para comunicación con el backend:

- **Métodos principales:**
  - `getAlertsInRadius(lat, lng, radius)`: Obtener alertas por proximidad
  - `getSensors()`: Obtener todos los sensores
  - `createSensor(sensorData)`: Crear sensor con ubicación
  - `getCurrentLocation()`: Obtener ubicación del usuario
  - `calculateDistance(lat1, lng1, lat2, lng2)`: Calcular distancia

## 🔄 Flujo de Datos

1. **Usuario interactúa con el mapa** (clic o botón "Mi ubicación")
2. **Frontend obtiene coordenadas** y radio seleccionado
3. **Petición HTTP** al endpoint `/api/alertas` con parámetros geoespaciales
4. **Backend ejecuta consulta MongoDB** con operador `$near`
5. **MongoDB retorna alertas** dentro del radio especificado
6. **Backend procesa resultados** y calcula distancias
7. **Frontend recibe datos** y actualiza marcadores en el mapa
8. **Actualización automática** cada 30 segundos

## 🚀 Uso del Módulo

### 1. Configurar Sensores

```python
from app.services.geospatial_service import geospatial_service

# Crear sensor con ubicación
result = geospatial_service.create_sensor_with_location(
    sensor_id="sensor_001",
    lat=-34.6037,
    lng=-58.3816,
    nombre="Sensor Centro",
    descripcion="Sensor principal"
)
```

### 2. Guardar Mediciones

```python
# Guardar medición con datos geoespaciales
result = geospatial_service.save_measurement_with_location(
    sensor_id="sensor_001",
    nivel=25.5,
    estado="normal",
    lat=-34.6037,
    lng=-58.3816
)
```

### 3. Consultar Alertas

```python
# Obtener alertas en radio de 5km
result = geospatial_service.get_alerts_in_radius(
    lat=-34.6037,
    lng=-58.3816,
    radius_meters=5000
)
```

## 🧪 Pruebas

### Script de Inicialización

```bash
cd backend/backend-flask
python setup_geospatial_data.py
```

Este script:
- Crea 5 sensores de prueba en Buenos Aires
- Genera mediciones de los últimos 7 días
- Prueba las consultas geoespaciales
- Verifica la funcionalidad completa

### Pruebas Manuales

1. **Abrir el dashboard** en `http://localhost:5173`
2. **Hacer clic en el mapa** para buscar alertas
3. **Usar el botón "Mi ubicación"** para geolocalización
4. **Cambiar el radio** y ver cómo se actualizan las alertas
5. **Verificar actualización automática** cada 30 segundos

## 🔧 Configuración Avanzada

### Personalizar Radios de Búsqueda

En `GeospatialMap.vue`:

```javascript
// Modificar opciones de radio
const radiusOptions = [
  { value: 500, label: '500m' },
  { value: 1000, label: '1km' },
  { value: 2000, label: '2km' },
  { value: 5000, label: '5km' },
  { value: 10000, label: '10km' }
]
```

### Personalizar Colores de Alertas

En `geospatialService.js`:

```javascript
getAlertColor(estado) {
  switch (estado) {
    case 'inundacion':
      return '#ef4444' // rojo
    case 'sequia':
      return '#f59e0b' // naranja
    case 'normal':
      return '#10b981' // verde
    default:
      return '#6b7280' // gris
  }
}
```

## 📈 Rendimiento

### Optimizaciones Implementadas

1. **Índices 2dsphere**: Consultas geoespaciales optimizadas
2. **Límite de resultados**: Máximo 100 alertas por consulta
3. **Caché de ubicación**: Evita consultas repetidas innecesarias
4. **Actualización inteligente**: Solo actualiza si hay ubicación válida

### Métricas Esperadas

- **Tiempo de consulta**: < 100ms para radios < 10km
- **Memoria**: < 50MB adicionales para el módulo
- **Ancho de banda**: ~1KB por consulta de alertas

## 🛠️ Mantenimiento

### Monitoreo

- **Health Check**: `GET /api/geospatial/health`
- **Logs**: Verificar logs de `geospatial_service`
- **Métricas**: Monitorear tiempo de respuesta de consultas

### Limpieza de Datos

```javascript
// Eliminar mediciones antiguas (> 30 días)
db.mediciones.deleteMany({
  "timestamp": {
    "$lt": new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  }
})
```

## 🔒 Seguridad

### Validaciones Implementadas

- **Coordenadas**: Validación de rangos lat/lng
- **Radio**: Límite máximo de 100km
- **Autenticación**: JWT requerido para todos los endpoints
- **Sanitización**: Validación de tipos de datos

### Consideraciones de Privacidad

- **Geolocalización**: Solo con consentimiento del usuario
- **Datos sensibles**: No se almacenan ubicaciones de usuarios
- **Logs**: No incluyen coordenadas exactas en logs

## 🚀 Próximas Mejoras

### Funcionalidades Adicionales

1. **Notificaciones Push**: Integración con Firebase/OneSignal
2. **Histórico de Ubicaciones**: Seguimiento de consultas del usuario
3. **Filtros Avanzados**: Por tipo de alerta, fecha, etc.
4. **Exportación**: Descargar datos en CSV/GeoJSON
5. **Clustering**: Agrupación de marcadores cercanos

### Optimizaciones

1. **WebSockets**: Actualizaciones en tiempo real
2. **Caché Redis**: Almacenamiento temporal de consultas frecuentes
3. **CDN**: Servir tiles de mapas desde CDN
4. **PWA**: Funcionalidad offline básica

---

## 📞 Soporte

Para dudas o problemas con el módulo geoespacial:

1. **Verificar logs** del backend Flask
2. **Comprobar conexión** a MongoDB
3. **Validar índices** 2dsphere
4. **Revisar permisos** de geolocalización en el navegador

**Documentación actualizada**: Enero 2024
**Versión del módulo**: 1.0.0
