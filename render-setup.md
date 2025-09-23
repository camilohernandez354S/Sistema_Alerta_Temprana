# Configuración de Despliegue en Render

## Variables de Entorno Necesarias:

### Backend (sat-backend):
- `FLASK_ENV=production`
- `SECRET_KEY` (generar automáticamente)
- `MONGO_URI` (conectar a base de datos)
- `CORS_ORIGINS=https://sat-frontend.onrender.com`

### Frontend (sat-frontend):
- `VITE_API_URL=https://sat-backend.onrender.com`

## Pasos de Despliegue:

1. **Subir código a GitHub**
2. **Conectar repositorio en Render**
3. **Crear servicios según render.yaml**
4. **Configurar variables de entorno**
5. **Desplegar**

## Nota sobre Arduino:
El servicio Arduino Reader NO se puede desplegar en la nube ya que requiere acceso físico al puerto serial. Solo funciona en desarrollo local.
