@echo off
echo ========================================
echo Verificacion de Configuracion Arduino
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0verificar-config-arduino.ps1"

pause

