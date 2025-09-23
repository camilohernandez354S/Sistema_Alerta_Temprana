# 🚀 Configuración de Gunicorn - Sistema de Alerta Temprana

## ✅ **Archivos Creados/Actualizados**

### 1. **`gunicorn.conf.py`** - Configuración Principal
- ✅ Configuración optimizada para producción
- ✅ Workers automáticos según CPU
- ✅ Timeouts configurados
- ✅ Logs detallados
- ✅ Hooks para monitoreo

### 2. **`wsgi.py`** - Punto de Entrada WSGI
- ✅ Aplicación WSGI para Gunicorn
- ✅ Carga de variables de entorno
- ✅ Configuración de Flask

### 3. **`Procfile`** - Comando de Inicio
- ✅ Comando para Render/Heroku
- ✅ Usa configuración personalizada

### 4. **`run.py`** - Servidor de Desarrollo
- ✅ Solo para desarrollo local
- ✅ Información detallada de inicio

### 5. **`requirements.txt`** - Dependencias Backend
- ✅ Dependencias específicas del backend
- ✅ Gunicorn incluido

## 🔧 **Configuración de Gunicorn**

### **Workers y Concurrencia:**
```python
workers = multiprocessing.cpu_count() * 2 + 1  # Automático según CPU
worker_class = 'sync'                          # Para Flask
worker_connections = 1000                      # Conexiones por worker
```

### **Timeouts:**
```python
timeout = 120                    # Timeout de request
keepalive = 2                    # Keep-alive
graceful_timeout = 30            # Tiempo para cerrar gracefully
```

### **Logs:**
```python
accesslog = '-'                  # Logs de acceso a stdout
errorlog = '-'                   # Logs de error a stdout
loglevel = 'info'                # Nivel de log
```

## 🚀 **Comandos de Ejecución**

### **Desarrollo Local:**
```bash
cd backend/backend-flask
python run.py
```

### **Producción con Gunicorn:**
```bash
cd backend/backend-flask
gunicorn --config gunicorn.conf.py wsgi:application
```

### **Render (Automático):**
```yaml
startCommand: cd backend/backend-flask && gunicorn --config gunicorn.conf.py wsgi:application
```

## 📊 **Variables de Entorno para Gunicorn**

### **Opcionales (con valores por defecto):**
```bash
PORT=5000                        # Puerto del servidor
WEB_CONCURRENCY=auto             # Número de workers
GUNICORN_TIMEOUT=120             # Timeout de requests
LOG_LEVEL=info                   # Nivel de logging
```

### **Requeridas:**
```bash
SECRET_KEY=tu_clave_secreta
MONGO_URI=mongodb://...
MONGO_DB=sat_database
FLASK_ENV=production
```

## 🔍 **Monitoreo y Logs**

### **Logs Disponibles:**
- ✅ **Access Logs**: Todas las peticiones HTTP
- ✅ **Error Logs**: Errores de la aplicación
- ✅ **Gunicorn Logs**: Estado de workers
- ✅ **Application Logs**: Logs de Flask

### **Hooks de Monitoreo:**
- ✅ `on_starting`: Servidor iniciando
- ✅ `when_ready`: Servidor listo
- ✅ `post_fork`: Worker creado
- ✅ `worker_int`: Worker interrumpido

## 🎯 **Optimizaciones Incluidas**

### **Rendimiento:**
- ✅ **Preload App**: Carga la app antes de fork
- ✅ **Worker TMP Dir**: Usa memoria compartida
- ✅ **Max Requests**: Recicla workers automáticamente
- ✅ **Keep Alive**: Reutiliza conexiones

### **Seguridad:**
- ✅ **Request Limits**: Limita tamaño de requests
- ✅ **Graceful Shutdown**: Cierre controlado
- ✅ **Worker Isolation**: Workers independientes

## 📋 **Estructura de Archivos**

```
backend/backend-flask/
├── gunicorn.conf.py          # Configuración de Gunicorn
├── wsgi.py                   # Punto de entrada WSGI
├── run.py                    # Servidor de desarrollo
├── requirements.txt          # Dependencias del backend
├── app/                      # Aplicación Flask
│   ├── __init__.py          # Factory de la app
│   ├── api/                 # Rutas API
│   └── services/            # Servicios
└── ...
```

## 🚀 **Despliegue en Render**

### **1. Subir Código:**
```bash
git add .
git commit -m "Configuración completa de Gunicorn"
git push origin main
```

### **2. Render Configurará Automáticamente:**
- ✅ Usará `render.yaml` para configuración
- ✅ Ejecutará `gunicorn --config gunicorn.conf.py wsgi:application`
- ✅ Configurará variables de entorno
- ✅ Creará workers automáticamente

### **3. Verificar Despliegue:**
```bash
# Estado del sistema
curl https://tu-backend.onrender.com/api/health

# Estado de la base de datos
curl https://tu-backend.onrender.com/api/health/database
```

## ⚡ **Ventajas de esta Configuración**

1. **Rendimiento**: Workers optimizados según CPU
2. **Escalabilidad**: Maneja múltiples requests simultáneos
3. **Monitoreo**: Logs detallados y hooks
4. **Seguridad**: Límites de request y workers aislados
5. **Mantenimiento**: Recicla workers automáticamente
6. **Compatibilidad**: Funciona en Render, Heroku, etc.

## 🎉 **¡Listo para Producción!**

Tu Sistema de Alerta Temprana ahora tiene una configuración de Gunicorn profesional y optimizada para producción en la nube.

**Características:**
- ✅ **Alto rendimiento** con workers automáticos
- ✅ **Logs detallados** para monitoreo
- ✅ **Configuración segura** con límites
- ✅ **Fácil despliegue** en Render
- ✅ **Escalabilidad** automática
