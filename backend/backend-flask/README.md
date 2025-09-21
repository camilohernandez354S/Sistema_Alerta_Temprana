# Sistema de Monitoreo de Nivel de Agua - Backend

Backend Flask para el sistema de monitoreo de nivel de agua con Arduino.

## 🏗️ Arquitectura

El proyecto sigue las mejores prácticas de Flask con una arquitectura en capas:

```
app/
├── api/                    # Endpoints de la API
├── controllers/            # Controladores (lógica de presentación)
├── services/              # Servicios de negocio
├── repositories/          # Acceso a datos (Repository Pattern)
├── models/               # Modelos de datos (Pydantic)
├── utils/                # Utilidades y middleware
└── factory.py            # Dependency Injection Factory

config/                   # Configuraciones por entorno
tests/                   # Tests unitarios e integración
logs/                    # Archivos de log
```

## 🚀 Características

- **Application Factory Pattern**: Configuración flexible por entornos
- **Dependency Injection**: Factory pattern para gestión de dependencias
- **Repository Pattern**: Separación clara de acceso a datos
- **Validation**: Validación robusta con Pydantic
- **Error Handling**: Manejo centralizado de errores
- **Logging**: Sistema de logging estructurado con rotación
- **Testing**: Suite completa de tests
- **Blockchain**: Integridad de datos con blockchain simple
- **AI Predictions**: Predicciones con machine learning

## 🛠️ Instalación

### Prerrequisitos

- Python 3.9+
- MongoDB
- pip

### Configuración

1. **Clonar y navegar al directorio:**
```bash
cd backend/backend-flask
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

5. **Iniciar MongoDB:**
```bash
# Asegúrate de que MongoDB esté ejecutándose
mongod
```

## 🎯 Uso

### Desarrollo

```bash
# Modo desarrollo
export FLASK_ENV=development
python run.py
```

### Producción

```bash
# Modo producción
export FLASK_ENV=production
python run.py
```

### Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_sensor_api.py
```

## 📡 API Endpoints

### Sensores

- `POST /api/sensor/lectura` - Procesar nueva lectura
- `POST /api/sensor/lecturas` - Procesar múltiples lecturas
- `GET /api/sensor/todas-lecturas` - Obtener todas las lecturas
- `GET /api/sensor/ultima-lectura` - Obtener última lectura
- `GET /api/sensor/rango-tiempo/<rango>` - Lecturas por tiempo (1h, 24h, 7d)
- `GET /api/sensor/estadisticas-diarias` - Estadísticas del día
- `GET /api/sensor/estadisticas-estados` - Estadísticas por estado
- `GET /api/sensor/predicciones` - Predicciones de IA
- `GET /api/sensor/verify-blockchain` - Verificar integridad blockchain

### Sistema

- `GET /api/health` - Health check

## 🔧 Configuración

### Variables de Entorno

```env
# Aplicación
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-secret-key

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=sensor_database
MONGO_COLLECTION=sensor_readings

# CORS
CORS_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Entornos

- **Development**: Debug activado, logging detallado
- **Production**: Optimizado para producción, validaciones estrictas
- **Testing**: Configuración para tests automatizados

## 📊 Monitoreo

### Logs

Los logs se almacenan en el directorio `logs/` con rotación automática:

- `app.log` - Log principal
- Rotación cada 10MB
- Máximo 5 archivos de respaldo

### Health Check

```bash
curl http://localhost:5000/api/health
```

Respuesta:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "blockchain": "ok"
  },
  "timestamp": "2025-01-20T10:30:00"
}
```

## 🧪 Testing

### Estructura de Tests

```
tests/
├── conftest.py           # Configuración pytest
├── test_sensor_api.py    # Tests de API
├── test_services.py      # Tests de servicios
└── test_repositories.py  # Tests de repositorios
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_sensor_api.py::TestSensorAPI::test_health_check
```

## 🔐 Seguridad

- Validación de entrada con Pydantic
- Sanitización de datos
- Manejo seguro de errores
- Variables de entorno para secretos
- CORS configurado
- Rate limiting (opcional)

## 📈 Performance

- Connection pooling con MongoDB
- Índices optimizados en base de datos
- Logging asíncrono
- Respuestas paginadas
- Caché (futuro)

## 🐛 Debugging

### Logs de Debug

```bash
export LOG_LEVEL=DEBUG
python run.py
```

### Troubleshooting

1. **Error de conexión MongoDB**: Verificar que MongoDB esté ejecutándose
2. **Import errors**: Verificar que todas las dependencias estén instaladas
3. **Port already in use**: Cambiar FLASK_PORT en .env

## 🚀 Deployment

### Docker (Recomendado)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

### Systemd Service

```ini
[Unit]
Description=Sensor API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/app
ExecStart=/path/to/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Changelog

### v2.0.0 - Reorganización Arquitectónica
- Implementación de Application Factory Pattern
- Repository Pattern para acceso a datos
- Dependency Injection con Factory
- Sistema de logging mejorado
- Suite completa de tests
- Documentación de API
- Manejo centralizado de errores

### v1.0.0 - Versión Inicial
- API básica de sensores
- Integración con MongoDB
- Blockchain para integridad
- Predicciones básicas con ML
