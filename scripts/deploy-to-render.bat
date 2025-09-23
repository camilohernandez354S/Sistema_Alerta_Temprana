@echo off
echo ==========================================
echo DESPLIEGUE AUTOMÁTICO A RENDER
echo ==========================================

echo.
echo 📋 PASOS PREVIOS:
echo    1. Asegúrate de tener una cuenta en Render.com
echo    2. Conecta tu repositorio de GitHub
echo    3. Configura las variables de entorno
echo.

echo 🔧 CONFIGURANDO ARCHIVOS DE DESPLIEGUE...

REM Copiar configuración de producción
copy config\production.env .env
echo ✅ Archivo .env configurado para producción

REM Copiar configuración del frontend
copy config\frontend-production.env frontend\.env.production
echo ✅ Variables de entorno del frontend configuradas

echo.
echo 📝 VARIABLES DE ENTORNO A CONFIGURAR EN RENDER:
echo.
echo BACKEND (sat-backend):
echo   - SECRET_KEY: Generar automáticamente
echo   - MONGO_URI: Conectar a base de datos sat-mongo
echo   - CORS_ORIGINS: https://sat-frontend.onrender.com
echo   - ARDUINO_ENABLED: false
echo.
echo FRONTEND (sat-frontend):
echo   - VITE_API_URL: https://sat-backend.onrender.com
echo   - VITE_APP_TITLE: Sistema de Alerta Temprana
echo.
echo DATABASE (sat-mongo):
echo   - Usuario: sat_user
echo   - Base de datos: sat_database
echo.

echo 🚀 PASOS PARA DESPLEGAR:
echo    1. Sube este código a GitHub
echo    2. Ve a render.com y crea un nuevo proyecto
echo    3. Conecta tu repositorio de GitHub
echo    4. Render detectará automáticamente el archivo render.yaml
echo    5. Configura las variables de entorno
echo    6. Despliega
echo.

echo ⚠️  IMPORTANTE:
echo    - El servicio Arduino NO se desplegará (requiere hardware físico)
echo    - Solo funcionará el backend y frontend
echo    - Para desarrollo local completo usa: docker-compose up
echo.

pause
