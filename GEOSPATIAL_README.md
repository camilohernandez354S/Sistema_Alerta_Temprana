# 🗺️ Módulo de Alertas Georreferenciadas

## Descripción

Módulo especializado para el Sistema de Alerta Temprana que implementa funcionalidades geoespaciales, permitiendo consultar alertas por proximidad geográfica con área circular configurable.

## ✨ Características Principales

- **🗺️ Mapas Interactivos**: Integración con Leaflet para visualización geográfica
- **📍 Geolocalización**: Obtención automática de ubicación del usuario
- **🔍 Búsqueda por Proximidad**: Consultas geoespaciales con radio configurable
- **⚡ Actualización Automática**: Refresco cada 30 segundos sin interrupciones
- **🎨 Interfaz Intuitiva**: Controles simples y visualización clara de alertas

## 🚀 Inicio Rápido

### 1. Configurar Backend

```bash
# Instalar dependencias
cd backend/backend-flask
pip install -r requirements.txt

# Inicializar datos de prueba
python setup_geospatial_data.py

# Iniciar servidor
python run.py
```

### 2. Configurar Frontend

```bash
# Instalar dependencias
cd frontend
npm install

# Iniciar servidor de desarrollo
npm run dev
```

### 3. Usar el Módulo

1. **Abrir el dashboard** en `http://localhost:5173`
2. **Hacer clic en el mapa** para buscar alertas en esa ubicación
3. **Usar "Mi ubicación"** para centrar el mapa en tu posición actual
4. **Cambiar el radio** (1km, 2km, 5km, 10km, 20km) según necesites
5. **Ver la lista de alertas** encontradas en el área seleccionada

## 📡 API Endpoints

### Consultar Alertas por Proximidad

```bash
GET /api/alertas?lat={lat}&lng={lng}&radio={metros}
```

**Ejemplo:**
```bash
curl "http://localhost:5000/api/alertas?lat=-34.6037&lng=-58.3816&radio=5000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Obtener Sensores

```bash
GET /api/sensores
```

### Crear Sensor

```bash
POST /api/sensores
Content-Type: application/json

{
  "sensor_id": "sensor_001",
  "lat": -34.6037,
  "lng": -58.3816,
  "nombre": "Sensor Centro",
  "descripcion": "Sensor principal"
}
```

## 🗺️ Consultas Geoespaciales en MongoDB

### Consulta Básica

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

### Crear Índices

```javascript
db.mediciones.createIndex({"location": "2dsphere"})
db.sensores.createIndex({"location": "2dsphere"})
```

## 🧪 Pruebas

### Ejecutar Pruebas de Integración

```bash
cd backend/backend-flask
python test_geospatial_integration.py
```

### Verificar Funcionamiento

1. **Backend**: `http://localhost:5000/api/health`
2. **Módulo Geoespacial**: `http://localhost:5000/api/geospatial/health`
3. **Frontend**: `http://localhost:5173`

## 📊 Estructura de Datos

### Mediciones con Datos Geoespaciales

```json
{
  "_id": "ObjectId",
  "sensor_id": "string",
  "location": {
    "type": "Point",
    "coordinates": [lng, lat]
  },
  "nivel": "float",
  "estado": "sequia|normal|inundacion",
  "timestamp": "ISODate"
}
```

### Sensores con Ubicación

```json
{
  "_id": "ObjectId",
  "sensor_id": "string",
  "location": {
    "type": "Point",
    "coordinates": [lng, lat]
  },
  "nombre": "string",
  "descripcion": "string",
  "activo": "boolean",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

## 🎨 Componentes Frontend

### GeospatialMap.vue

- **Props**: `initialLat`, `initialLng`, `initialZoom`
- **Funcionalidades**: Mapa interactivo, selección de radio, geolocalización
- **Actualización**: Automática cada 30 segundos

### geospatialService.js

- **Métodos**: `getAlertsInRadius()`, `getSensors()`, `createSensor()`
- **Utilidades**: Cálculo de distancias, formateo de datos
- **Estado**: Reactivo con Vue 3

## 🔧 Configuración Avanzada

### Personalizar Radios de Búsqueda

```javascript
// En GeospatialMap.vue
const radiusOptions = [
  { value: 500, label: '500m' },
  { value: 1000, label: '1km' },
  { value: 2000, label: '2km' },
  { value: 5000, label: '5km' },
  { value: 10000, label: '10km' }
]
```

### Personalizar Colores de Alertas

```javascript
// En geospatialService.js
getAlertColor(estado) {
  switch (estado) {
    case 'inundacion': return '#ef4444'  // rojo
    case 'sequia': return '#f59e0b'      // naranja
    case 'normal': return '#10b981'      // verde
    default: return '#6b7280'            // gris
  }
}
```

## 📈 Rendimiento

- **Consultas**: < 100ms para radios < 10km
- **Memoria**: < 50MB adicionales
- **Ancho de banda**: ~1KB por consulta
- **Actualización**: Cada 30 segundos automáticamente

## 🛠️ Mantenimiento

### Health Checks

- **Backend**: `GET /api/health`
- **Geoespacial**: `GET /api/geospatial/health`

### Limpieza de Datos

```javascript
// Eliminar mediciones antiguas (> 30 días)
db.mediciones.deleteMany({
  "timestamp": {
    "$lt": new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  }
})
```

## 🚀 Próximas Mejoras

- **Notificaciones Push**: Integración con Firebase
- **Histórico de Ubicaciones**: Seguimiento de consultas
- **Filtros Avanzados**: Por tipo, fecha, etc.
- **Exportación**: CSV/GeoJSON
- **Clustering**: Agrupación de marcadores

## 📞 Soporte

### Problemas Comunes

1. **Mapa no carga**: Verificar que Leaflet esté instalado
2. **No hay alertas**: Ejecutar `setup_geospatial_data.py`
3. **Error de geolocalización**: Verificar permisos del navegador
4. **Consultas lentas**: Verificar índices 2dsphere en MongoDB

### Logs

- **Backend**: Logs de Flask en consola
- **Frontend**: Console del navegador
- **MongoDB**: Logs de consultas geoespaciales

---

**Desarrollado con ❤️ siguiendo principios SRP, KISS y DRY**

**Versión**: 1.0.0  
**Última actualización**: Enero 2024
