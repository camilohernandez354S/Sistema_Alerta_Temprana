@echo off
echo ============================================================
echo Instalando dependencias para leer_serial.py
echo ============================================================
echo.

echo [1/2] Instalando pyserial...
py -m pip install pyserial
if errorlevel 1 (
    echo Error instalando pyserial
    pause
    exit /b 1
)

echo.
echo [2/2] Instalando python-dotenv...
py -m pip install python-dotenv
if errorlevel 1 (
    echo Error instalando python-dotenv
    pause
    exit /b 1
)

echo.
echo [3/3] Instalando requests...
py -m pip install requests
if errorlevel 1 (
    echo Error instalando requests
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Dependencias instaladas correctamente!
echo ============================================================
echo.
echo Ahora puedes ejecutar:
echo   py leer_serial.py
echo.
pause

