# Documentación de API - Sistema de Alerta Temprana

## Resumen

Esta API proporciona endpoints para el monitoreo de niveles de agua y predicciones inteligentes para el sistema de alerta temprana.

## Configuración CORS

La API está configurada para aceptar requests desde:
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (Vue CLI)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:8080`

## Endpoints Principales

### 1. Obtener Predicciones de Nivel de Agua

**Endpoint:** `GET /api/sensor/predicciones`

**Descripción:** Genera predicciones robustas de nivel de agua usando análisis de señales y limpieza de datos.

**Query Parameters:**
- `horizons` (opcional): Lista de horizontes en minutos separados por comas (default: `30,60,180`)

**Ejemplo de Request:**
```bash
curl -X GET "http://localhost:5000/api/sensor/predicciones?horizons=30,60,180" \
  -H "Content-Type: application/json"
```

**Ejemplo de Response (200 OK):**
```json
{
  "meta": {
    "generated_at": "2025-01-21T15:30:00.000Z",
    "window_used_minutes": 120,
    "horizons": [30, 60, 180],
    "data_points_used": 45
  },
  "current": {
    "nivel_cm": 45.2,
    "estado": "Normal",
    "tendencia": "sube",
    "pendiente_cm_por_h": 5.4
  },
  "predicciones": [
    {
      "horizon_min": 30,
      "nivel_cm": 48.0,
      "estado": "Normal",
      "confianza": 0.74
    },
    {
      "horizon_min": 60,
      "nivel_cm": 50.9,
      "estado": "Normal",
      "confianza": 0.69
    },
    {
      "horizon_min": 180,
      "nivel_cm": 59.6,
      "estado": "Normal",
      "confianza": 0.55
    }
  ]
}
```

**Ejemplo de Response (Error):**
```json
{
  "error": {
    "message": "No hay suficientes datos históricos para hacer predicciones",
    "code": "INSUFFICIENT_DATA"
  }
}
```

### 2. Obtener Lecturas del Sensor

**Endpoint:** `GET /api/sensor/todas-lecturas`

**Descripción:** Obtiene lecturas del sensor con parámetros de filtrado opcionales.

**Query Parameters:**
- `limit` (opcional): Número máximo de lecturas (default: 500, max: 1000)
- `since` (opcional): Timestamp ISO desde cuando obtener lecturas
- `order` (opcional): Orden de resultados (`asc` o `desc`, default: `desc`)

**Ejemplo de Request:**
```bash
curl -X GET "http://localhost:5000/api/sensor/todas-lecturas?limit=100&order=asc" \
  -H "Content-Type: application/json"
```

**Ejemplo de Response (200 OK):**
```json
{
  "lecturas": [
    {
      "id": "507f1f77bcf86cd799439011",
      "nivel_cm": 45.0,
      "estado": "Normal",
      "timestamp": "2025-01-21T15:10:00Z"
    },
    {
      "id": "507f1f77bcf86cd799439012",
      "nivel_cm": 44.8,
      "estado": "Normal",
      "timestamp": "2025-01-21T15:15:00Z"
    }
  ],
  "total": 100,
  "limit": 100,
  "order": "asc"
}
```

### 3. Obtener Última Lectura

**Endpoint:** `GET /api/sensor/ultima-lectura`

**Descripción:** Obtiene la lectura más reciente del sensor.

**Ejemplo de Request:**
```bash
curl -X GET "http://localhost:5000/api/sensor/ultima-lectura" \
  -H "Content-Type: application/json"
```

**Ejemplo de Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "nivel_cm": 45.2,
  "estado": "Normal",
  "timestamp": "2025-01-21T15:30:00Z"
}
```

### 4. Obtener Lecturas por Rango de Tiempo

**Endpoint:** `GET /api/sensor/rango-tiempo/{rango}`

**Descripción:** Obtiene lecturas en un rango de tiempo específico.

**Path Parameters:**
- `rango`: Rango de tiempo (`1h`, `24h`, `7d`)

**Ejemplo de Request:**
```bash
curl -X GET "http://localhost:5000/api/sensor/rango-tiempo/24h" \
  -H "Content-Type: application/json"
```

### 5. Health Check

**Endpoint:** `GET /api/health`

**Descripción:** Verifica el estado de salud del sistema.

**Ejemplo de Request:**
```bash
curl -X GET "http://localhost:5000/api/health" \
  -H "Content-Type: application/json"
```

**Ejemplo de Response (200 OK):**
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "blockchain": "ok"
  },
  "timestamp": "2025-01-21T15:30:00.000Z"
}
```

## Estados de Nivel de Agua

Los niveles de agua se clasifican según los siguientes umbrales (configurables):

- **Sequía**: ≤ 20 cm (configurable via `DROUGHT_MAX_CM`)
- **Normal**: 20 cm < nivel < 60 cm
- **Inundación**: ≥ 60 cm (configurable via `NORMAL_MAX_CM`)

## Códigos de Error

### Errores de Predicción
- `PREDICTION_FAILED`: Error interno en el servicio de predicción
- `INSUFFICIENT_DATA`: No hay suficientes datos históricos

### Errores de Validación
- `400 Bad Request`: Parámetros inválidos
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error interno del servidor

## Uso desde Vue.js (Frontend)

### Ejemplo de Consumo de Predicciones

```javascript
// services/predictionService.js
export class PredictionService {
  constructor() {
    this.baseURL = 'http://localhost:5000/api';
  }

  async getPredictions(horizons = [30, 60, 180]) {
    try {
      const horizonsParam = horizons.join(',');
      const response = await fetch(
        `${this.baseURL}/sensor/predicciones?horizons=${horizonsParam}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Response is not JSON');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching predictions:', error);
      // Fallback para manejar errores
      return this.getFallbackPredictions();
    }
  }

  getFallbackPredictions() {
    return {
      meta: {
        generated_at: new Date().toISOString(),
        window_used_minutes: 0,
        horizons: [30, 60, 180],
        data_points_used: 0,
        warning: "Servicio temporalmente no disponible"
      },
      current: {
        nivel_cm: 0,
        estado: "Normal",
        tendencia: "estable",
        pendiente_cm_por_h: 0
      },
      predicciones: [
        {
          horizon_min: 30,
          nivel_cm: 0,
          estado: "Normal",
          confianza: 0.1
        }
      ]
    };
  }
}
```

### Ejemplo de Consumo de Lecturas

```javascript
// services/readingsService.js
export class ReadingsService {
  constructor() {
    this.baseURL = 'http://localhost:5000/api';
  }

  async getAllReadings(limit = 500, order = 'desc') {
    try {
      const response = await fetch(
        `${this.baseURL}/sensor/todas-lecturas?limit=${limit}&order=${order}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching readings:', error);
      return { lecturas: [], total: 0 };
    }
  }

  async getLatestReading() {
    try {
      const response = await fetch(`${this.baseURL}/sensor/ultima-lectura`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching latest reading:', error);
      return null;
    }
  }
}
```

### Ejemplo de Componente Vue

```vue
<template>
  <div class="predictions-dashboard">
    <div class="current-status">
      <h3>Estado Actual</h3>
      <div class="status-card">
        <p>Nivel: {{ current.nivel_cm }} cm</p>
        <p>Estado: {{ current.estado }}</p>
        <p>Tendencia: {{ current.tendencia }}</p>
      </div>
    </div>

    <div class="predictions">
      <h3>Predicciones</h3>
      <div v-for="pred in predictions" :key="pred.horizon_min" class="prediction-card">
        <h4>{{ pred.horizon_min }} minutos</h4>
        <p>Nivel predicho: {{ pred.nivel_cm }} cm</p>
        <p>Estado: {{ pred.estado }}</p>
        <p>Confianza: {{ (pred.confianza * 100).toFixed(1) }}%</p>
      </div>
    </div>
  </div>
</template>

<script>
import { PredictionService } from '@/services/predictionService.js';

export default {
  name: 'PredictionsDashboard',
  data() {
    return {
      current: {},
      predictions: [],
      predictionService: new PredictionService()
    };
  },
  async mounted() {
    await this.loadPredictions();
    // Actualizar cada 5 minutos
    setInterval(this.loadPredictions, 5 * 60 * 1000);
  },
  methods: {
    async loadPredictions() {
      try {
        const data = await this.predictionService.getPredictions();
        this.current = data.current;
        this.predictions = data.predicciones;
      } catch (error) {
        console.error('Error loading predictions:', error);
        // Usar datos de fallback
        this.current = { nivel_cm: 0, estado: 'Normal', tendencia: 'estable' };
        this.predictions = [];
      }
    }
  }
};
</script>
```

## Configuración del Sistema

### Variables de Entorno

```bash
# Configuración de predicciones
DROUGHT_MAX_CM=20.0
NORMAL_MAX_CM=60.0
REGRESSION_WINDOW_MIN=120
PREDICTION_MIN_DATA_POINTS=10

# Configuración de CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:8080

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar solo pruebas de predicción
pytest tests/test_prediction_service.py -v

# Ejecutar con cobertura
pytest tests/ --cov=app.services.prediction_service --cov-report=html
```

## Logging y Observabilidad

El sistema incluye logging contextual para predicciones:

```
2025-01-21 15:30:00 - prediction_service - INFO - INICIO_PREDICCION - data_points=45, horizons=[30, 60, 180], window_minutes=120
2025-01-21 15:30:00 - prediction_service - INFO - PREPROCESAMIENTO - original=50, limpios=45, outliers_removidos=2
2025-01-21 15:30:00 - prediction_service - INFO - ANALISIS_SENALES - pendiente=5.400, r_squared=0.742, tendencia=sube, puntos_ventana=24
2025-01-21 15:30:00 - prediction_service - INFO - PREDICCION_HORIZONTE - horizon_min=30, nivel_predicho=48.00, confianza=0.74, estado=Normal
2025-01-21 15:30:00 - prediction_service - INFO - PREDICCION_COMPLETA - total_horizons=3, confianza_promedio=0.66, tiempo_procesamiento=0.125s
```

## Mensajes de Commit Sugeridos

```
feat: implementar servicio de predicción robusto con limpieza de datos

- Agregar preprocesamiento con validación de esquema
- Implementar remoción de outliers con IQR
- Añadir interpolación de huecos temporales
- Incluir suavizado con media móvil
- Implementar análisis de señales con regresión lineal
- Agregar predicciones multi-horizonte con factor de amortiguación
- Incluir clasificación de estados configurables

feat: mejorar endpoint de predicciones con parámetros configurables

- Soporte para múltiples horizontes via query params
- Validación robusta de parámetros
- Respuestas estructuradas con metadata
- Manejo de errores consistente con códigos específicos

feat: normalizar endpoint de lecturas con filtrado avanzado

- Soporte para parámetros limit, since, order
- Formato de respuesta consistente
- Validación de timestamps ISO 8601
- Ordenamiento configurable

feat: agregar logging contextual para predicciones

- Logger específico para métricas de predicción
- Logging de preprocesamiento y análisis de señales
- Observabilidad de confianza y tiempos de procesamiento
- Formato estructurado para análisis

test: agregar suite completa de pruebas para predicciones

- Pruebas unitarias para preprocesamiento
- Tests de análisis de señales y tendencias
- Validación de predicciones multi-horizonte
- Pruebas de integración end-to-end
- Coverage de casos edge y manejo de errores

docs: documentar API completa con ejemplos de uso

- Documentación de endpoints con ejemplos curl
- Guía de integración para Vue.js
- Ejemplos de componentes y servicios
- Configuración y variables de entorno
- Logging y observabilidad
```
