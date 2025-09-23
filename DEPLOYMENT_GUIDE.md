# 🚀 Guía de Despliegue - Sistema de Alerta Temprana

## 📋 Resumen del Proyecto

Tu proyecto tiene la siguiente arquitectura:
- **Backend Flask**: API REST con servicios de alertas y geolocalización
- **Frontend Vue.js**: Interfaz de usuario moderna con Tailwind CSS
- **Arduino Reader**: Servicio para leer datos del puerto serial (solo local)
- **MongoDB**: Base de datos para almacenar mediciones y alertas

## 🎯 Opciones de Despliegue

### 1. **RENDER (RECOMENDADO)** ⭐

**Ventajas:**
- ✅ Soporte completo para arquitectura multi-servicio
- ✅ Despliegue automático desde GitHub
- ✅ Base de datos MongoDB incluida
- ✅ Configuración simple con `render.yaml`
- ✅ Plan gratuito generoso

**Limitaciones:**
- ❌ Arduino Reader no funciona (requiere hardware físico)

### 2. **VERCEL (Solo Frontend)**

**Ventajas:**
- ✅ Despliegue súper rápido del frontend
- ✅ CDN global automático

**Limitaciones:**
- ❌ No soporta backend Flask
- ❌ Necesitarías otra solución para el backend

## 🔧 Configuración Completa

### Archivos Creados:

1. **`render.yaml`** - Configuración automática de Render
2. **`config/`** - Variables de entorno para diferentes entornos
3. **`scripts/`** - Scripts de configuración automática
4. **`.gitignore`** - Actualizado para ignorar archivos sensibles

### Variables de Entorno Configuradas:

#### Backend (Flask):
- `FLASK_ENV`: Entorno de ejecución
- `SECRET_KEY`: Clave secreta para sesiones
- `MONGO_URI`: Conexión a MongoDB
- `CORS_ORIGINS`: Dominios permitidos
- `ARDUINO_ENABLED`: Habilitar/deshabilitar Arduino
- `LOG_LEVEL`: Nivel de logging

#### Frontend (Vue.js):
- `VITE_API_URL`: URL del backend
- `VITE_APP_TITLE`: Título de la aplicación
- `VITE_APP_VERSION`: Versión de la aplicación

## 🚀 Pasos para Desplegar en Render

### 1. Preparar el Proyecto
```bash
# Ejecutar script de configuración
scripts/setup-prod.bat  # Windows
# o
bash scripts/setup-env.sh  # Linux/Mac
```

### 2. Subir a GitHub
```bash
git add .
git commit -m "Configuración completa para despliegue"
git push origin main
```

### 3. Configurar en Render

1. **Crear cuenta en [render.com](https://render.com)**
2. **Conectar repositorio de GitHub**
3. **Render detectará automáticamente `render.yaml`**
4. **Configurar variables de entorno:**

#### Backend (sat-backend):
- `SECRET_KEY`: Generar automáticamente
- `MONGO_URI`: Conectar a base de datos sat-mongo
- `CORS_ORIGINS`: `https://sat-frontend.onrender.com`

#### Frontend (sat-frontend):
- `VITE_API_URL`: `https://sat-backend.onrender.com`
- `VITE_APP_TITLE`: `Sistema de Alerta Temprana`

### 4. Desplegar
- Render construirá y desplegará automáticamente
- Tiempo estimado: 15-20 minutos

## 🔄 Desarrollo Local

### Configurar entorno de desarrollo:
```bash
scripts/setup-dev.bat  # Windows
# o
bash scripts/setup-env.sh  # Linux/Mac (opción 1)
```

### Iniciar servicios:
```bash
docker-compose up
```

### Servicios disponibles:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:8080
- **MongoDB**: localhost:27017
- **Arduino**: Puerto COM11 (configurable)

## ⚠️ Consideraciones Importantes

### Arduino en Producción:
- **NO se puede desplegar** en la nube
- Requiere acceso físico al puerto serial
- Solo funciona en desarrollo local
- Para producción, usar datos simulados o API externa

### Seguridad:
- Cambiar `SECRET_KEY` en producción
- Configurar HTTPS en producción
- Validar todas las entradas
- Implementar rate limiting

### Monitoreo:
- Configurar logs en producción
- Monitorear rendimiento
- Configurar alertas de error

## 📞 Soporte

Si tienes problemas con el despliegue:

1. **Revisar logs** en Render Dashboard
2. **Verificar variables de entorno**
3. **Comprobar conectividad** entre servicios
4. **Revisar configuración de CORS**

## 🎉 ¡Listo para Desplegar!

Con esta configuración tienes todo listo para desplegar tu Sistema de Alerta Temprana en Render. El proceso es automático y solo necesitas seguir los pasos de configuración en la plataforma.
