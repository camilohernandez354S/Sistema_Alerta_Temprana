@echo off
echo ========================================
echo Configuracion Arduino para Produccion
echo ========================================
echo.

set /p BACKEND_URL="Ingresa la URL del backend remoto (ej: https://sat-backend.onrender.com): "

if "%BACKEND_URL%"=="" (
    echo Error: Debes ingresar una URL valida
    pause
    exit /b 1
)

echo.
echo Actualizando .env...

REM Verificar que .env existe
if not exist .env (
    echo Error: No se encontro el archivo .env
    echo Copia config/example.env a .env primero
    pause
    exit /b 1
)

REM Actualizar FLASK_SERVER_URL en .env usando PowerShell
powershell -Command "(Get-Content .env) -replace 'FLASK_SERVER_URL=.*', 'FLASK_SERVER_URL=%BACKEND_URL%' | Set-Content .env"

echo .env actualizado
echo.

echo Generando configuracion WiFi para Arduino...
echo.

if exist backend\arduino\generar_config_wifi.py (
    python backend\arduino\generar_config_wifi.py
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Configuracion WiFi generada exitosamente!
        echo.
        echo Siguiente paso:
        echo    1. Abre backend/arduino/nivel_agua_wifi.ino en Arduino IDE
        echo    2. Verifica que wifi_config.h tenga la URL correcta
        echo    3. Sube el codigo al ESP8266/ESP32
        echo.
    ) else (
        echo Error al generar configuracion WiFi
    )
) else (
    echo Advertencia: No se encontro el script generar_config_wifi.py
)

pause

