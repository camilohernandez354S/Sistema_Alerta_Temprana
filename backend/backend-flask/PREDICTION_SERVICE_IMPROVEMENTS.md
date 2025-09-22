# Mejoras del Servicio de Predicción

## Resumen de Mejoras Implementadas

El servicio de predicción ha sido completamente reescrito con mejoras significativas en calidad, precisión y robustez.

## 1. Mejoras en la Calidad de las Predicciones

### Ventana Móvil de Datos Históricos
- **Implementación**: Ventana temporal configurable (default: 3 horas)
- **Beneficio**: Reduce el ruido de datos antiguos y mejora la precisión
- **Configuración**: `REGRESSION_WINDOW_MIN` en config.py

### Suavizado Exponencial
- **Implementación**: Suavizado exponencial con alpha=0.3 (configurable)
- **Beneficio**: Reduce ruido de alta frecuencia manteniendo tendencias
- **Configuración**: `EXPONENTIAL_SMOOTHING_ALPHA` en config.py

### Detección de Outliers Mejorada
- **Implementación**: IQR con factor conservador de 2.0 (vs 1.5 estándar)
- **Beneficio**: Elimina valores anómalos sin perder datos válidos
- **Configuración**: `OUTLIER_IQR_FACTOR` en config.py

### Regresión Lineal Avanzada
- **Implementación**: Scikit-learn si está disponible, numpy.polyfit como fallback
- **Beneficio**: Mayor precisión en el cálculo de pendientes y R²
- **Detección automática**: El servicio detecta si scikit-learn está disponible

## 2. Ajuste de Confianza Inteligente

### Cálculo de R²
- **Implementación**: R² calculado usando la regresión lineal
- **Uso**: Factor principal para determinar confianza del modelo
- **Rango**: 0.0 (sin correlación) a 1.0 (correlación perfecta)

### Ajuste por Cantidad de Datos
- **Implementación**: Confianza adicional basada en puntos disponibles
- **Fórmula**: `confianza = (R² * 0.7) + (densidad_datos * 0.3)`
- **Beneficio**: Menos confianza con pocos datos, más con muchos datos

### Límites de Confianza
- **Mínimo**: 0.3 (30%) - nunca completamente sin confianza
- **Máximo**: 0.95 (95%) - nunca completamente seguro
- **Configuración**: `MIN_CONFIDENCE` y `MAX_CONFIDENCE` en config.py

## 3. Predicciones Multi-Horizonte Mejoradas

### Factor de Amortiguación Adaptativo
- **Confianza < 0.5**: Factor 0.3 (muy conservador)
- **Confianza 0.5-0.7**: Factor 0.5 (moderado)
- **Confianza > 0.7**: Factor 0.7 (más agresivo)

### Aplanamiento Inteligente
- **Condición**: Tendencia débil (pendiente < 1.0 cm/h) O confianza baja
- **Efecto**: Predicciones se mantienen cerca del valor actual
- **Beneficio**: Evita predicciones erróneas en condiciones inciertas

### Horizontes Extendidos
- **Default**: [30, 60, 120, 180, 360] minutos
- **Configurable**: Via `DEFAULT_HORIZONS` en config.py
- **Beneficio**: Más opciones de predicción temporal

## 4. Clasificación de Estado Robusta

### Umbrales Configurables
- **Sequía**: ≤ 20 cm (configurable via `DROUGHT_MAX_CM`)
- **Normal**: 20-60 cm
- **Inundación**: ≥ 60 cm (configurable via `NORMAL_MAX_CM`)

### Clasificación Automática
- **Implementación**: Función `_classify_level(nivel_cm)`
- **Aplicación**: Tanto en estado actual como en predicciones
- **Consistencia**: Mismos umbrales en toda la aplicación

## 5. Estructura de Salida Mejorada

### Metadata Enriquecida
```json
{
  "meta": {
    "generated_at": "2025-01-21T15:30:00.000Z",
    "window_minutes": 180,
    "r2": 0.82,
    "points_used": 150,
    "horizons": [30, 60, 120, 180, 360],
    "sklearn_used": true
  }
}
```

### Información Actual Detallada
```json
{
  "current": {
    "nivel_cm": 42.3,
    "estado": "Normal",
    "tendencia": "sube",
    "pendiente_cm_por_h": 4.2
  }
}
```

### Predicciones Estructuradas
```json
{
  "predicciones": [
    {
      "horizon_min": 30,
      "nivel_cm": 44.4,
      "estado": "Normal",
      "confianza": 0.85
    }
  ]
}
```

## 6. Optimizaciones de Rendimiento

### Dependencias Mínimas
- **Obligatorio**: numpy (siempre disponible)
- **Opcional**: scikit-learn (mejor precisión si está disponible)
- **Fallback**: numpy.polyfit cuando scikit-learn no está disponible

### Tiempo de Ejecución
- **Objetivo**: < 1 segundo para 1000 puntos de datos
- **Optimización**: Ventana móvil reduce datos procesados
- **Eficiencia**: Algoritmos vectorizados con numpy

### Uso de Memoria
- **Optimización**: Procesamiento en lotes
- **Limpieza**: Datos temporales liberados automáticamente
- **Escalabilidad**: Maneja datasets grandes sin problemas

## 7. Logging y Observabilidad

### Logging Contextual
- **Inicio de predicción**: Datos, horizontes, ventana
- **Preprocesamiento**: Puntos originales, limpios, outliers removidos
- **Análisis de señales**: Pendiente, R², tendencia, puntos en ventana
- **Resultados**: Predicción individual por horizonte
- **Completación**: Horizontes totales, confianza promedio, tiempo

### Métricas Estructuradas
```
INICIO_PREDICCION - data_points=150, horizons=[30, 60, 120, 180, 360], window_minutes=180
PREPROCESAMIENTO - original=200, limpios=150, outliers_removidos=8
ANALISIS_SENALES - pendiente=4.200, r_squared=0.820, tendencia=sube, puntos_ventana=45
PREDICCION_HORIZONTE - horizon_min=30, nivel_predicho=44.4, confianza=0.85, estado=Normal
PREDICCION_COMPLETA - total_horizons=5, confianza_promedio=0.78, tiempo_procesamiento=0.125s
```

## 8. Configuración Avanzada

### Variables de Entorno
```bash
# Umbrales de clasificación
DROUGHT_MAX_CM=20.0
NORMAL_MAX_CM=60.0

# Horizontes de predicción
DEFAULT_HORIZONS=30,60,120,180,360

# Ventana de análisis
REGRESSION_WINDOW_MIN=180

# Parámetros de suavizado
EXPONENTIAL_SMOOTHING_ALPHA=0.3
OUTLIER_IQR_FACTOR=2.0

# Límites de confianza
MIN_CONFIDENCE=0.3
MAX_CONFIDENCE=0.95
```

## 9. Pruebas Comprehensivas

### Casos de Prueba Implementados
- **Series ascendentes**: Verificación de tendencia "sube"
- **Series descendentes**: Verificación de tendencia "baja"
- **Series estables**: Verificación de tendencia "estable"
- **Datos con outliers**: Verificación de eliminación de anomalías
- **Datos ruidosos**: Verificación de reducción de ruido
- **Datos insuficientes**: Verificación de fallback
- **Casos edge**: Valores extremos, datos vacíos
- **Rendimiento**: Dataset grandes (1000+ puntos)
- **Memoria**: Múltiples datasets grandes

### Cobertura de Pruebas
- **Unidad**: Métodos individuales
- **Integración**: Flujo completo end-to-end
- **Rendimiento**: Tiempo de ejecución y memoria
- **Robustez**: Manejo de errores y casos edge

## 10. Compatibilidad y Migración

### Retrocompatibilidad
- **Método legacy**: `generar_predicciones()` mantenido
- **Formato anterior**: Conversión automática a formato legacy
- **API existente**: Sin cambios en endpoints

### Migración Gradual
- **Configuración**: Valores por defecto seguros
- **Fallback**: Funcionamiento sin scikit-learn
- **Logging**: Información de versión y capacidades

## 11. Interpretación de Resultados

### Confianza
- **0.3-0.5**: Baja confianza - predicciones conservadoras
- **0.5-0.7**: Confianza moderada - predicciones equilibradas
- **0.7-0.95**: Alta confianza - predicciones más agresivas

### R² (Coeficiente de Determinación)
- **0.0-0.3**: Correlación débil - tendencia incierta
- **0.3-0.7**: Correlación moderada - tendencia discernible
- **0.7-1.0**: Correlación fuerte - tendencia clara

### Pendiente (cm/hora)
- **> 2.0**: Cambio rápido - requiere atención
- **0.5-2.0**: Cambio moderado - monitoreo normal
- **< 0.5**: Cambio lento - situación estable

## 12. Extensibilidad Futura

### Nuevos Algoritmos
- **Fácil integración**: Arquitectura modular
- **Múltiples modelos**: Soporte para diferentes algoritmos
- **Configuración**: Selección de modelo via config

### Nuevas Métricas
- **Confianza avanzada**: Factores adicionales
- **Intervalos de confianza**: Rangos de predicción
- **Alertas automáticas**: Umbrales de riesgo

### Integración ML
- **Scikit-learn**: Ya soportado
- **Otros frameworks**: TensorFlow, PyTorch (futuro)
- **Modelos pre-entrenados**: Soporte para modelos específicos

## Conclusión

Las mejoras implementadas transforman el servicio de predicción de una implementación básica a un sistema robusto y profesional, capaz de manejar datos reales con alta precisión y confiabilidad. El sistema mantiene compatibilidad hacia atrás mientras proporciona capacidades avanzadas para aplicaciones de producción.
