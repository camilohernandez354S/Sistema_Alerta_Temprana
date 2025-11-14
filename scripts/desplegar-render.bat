@echo off
echo ========================================
echo Despliegue en Render
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0desplegar-render.ps1" %*

pause

