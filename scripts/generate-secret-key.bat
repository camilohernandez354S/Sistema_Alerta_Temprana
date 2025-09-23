@echo off
echo ==========================================
echo GENERADOR DE SECRET_KEY SEGURA
echo ==========================================

echo.
echo Ejecutando generador de Python...
python scripts/generate-secret-key.py

echo.
echo ==========================================
echo CONFIGURACION EN RENDER:
echo ==========================================
echo.
echo 1. Ve a render.com
echo 2. Selecciona tu servicio backend
echo 3. Ve a Environment Variables
echo 4. Agrega: SECRET_KEY = [clave_generada]
echo 5. Guarda y redespliega
echo.
pause
