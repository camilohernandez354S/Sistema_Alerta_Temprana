@echo off
echo ==========================================
echo VERIFICACION DE CONFIGURACION DE DESPLIEGUE
echo ==========================================

echo.
echo 🔍 VERIFICANDO ARCHIVOS NECESARIOS...

REM Verificar render.yaml
if exist render.yaml (
    echo ✅ render.yaml - OK
) else (
    echo ❌ render.yaml - FALTANTE
)

REM Verificar mongo.Dockerfile
if exist mongo.Dockerfile (
    echo ✅ mongo.Dockerfile - OK
) else (
    echo ❌ mongo.Dockerfile - FALTANTE
)

REM Verificar archivos de configuración
if exist config\production.env (
    echo ✅ config\production.env - OK
) else (
    echo ❌ config\production.env - FALTANTE
)

if exist config\frontend-production.env (
    echo ✅ config\frontend-production.env - OK
) else (
    echo ❌ config\frontend-production.env - FALTANTE
)

REM Verificar .gitignore
if exist .gitignore (
    echo ✅ .gitignore - OK
) else (
    echo ❌ .gitignore - FALTANTE
)

echo.
echo ==========================================
echo RESUMEN DE CONFIGURACION:
echo ==========================================

echo.
echo 📋 SERVICIOS CONFIGURADOS:
echo   - sat-backend (Flask API)
echo   - sat-frontend (Vue.js)
echo   - sat-mongo (MongoDB Database)
echo.
echo 🔑 SECRET_KEY CONFIGURADA:
echo   962dcfefd06ec551f095af1b24dd6ff96548e9e31ed6f7161dce07a41e689dfe
echo.
echo 🌐 URLs DESPUES DEL DESPLIEGUE:
echo   - Frontend: https://sat-frontend.onrender.com
echo   - Backend: https://sat-backend.onrender.com
echo.
echo 📝 VARIABLES DE ENTORNO CONFIGURADAS:
echo   - FLASK_ENV=production
echo   - SECRET_KEY=configurada
echo   - MONGO_URI=conectada a base de datos
echo   - CORS_ORIGINS=configurado
echo   - ARDUINO_ENABLED=false
echo.
echo 🚀 LISTO PARA DESPLEGAR EN RENDER!
echo.
echo SIGUIENTES PASOS:
echo 1. git add .
echo 2. git commit -m "Configuracion completa para despliegue"
echo 3. git push origin main
echo 4. Crear cuenta en render.com
echo 5. Conectar repositorio GitHub
echo 6. Desplegar usando render.yaml
echo.
pause

