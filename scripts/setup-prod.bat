@echo off
echo ==========================================
echo CONFIGURANDO ENTORNO DE PRODUCCIÓN
echo ==========================================

REM Copiar archivo de configuración de producción
copy config\production.env .env

echo.
echo ✅ Archivo .env creado para producción
echo.
echo 📝 IMPORTANTE: Configura estas variables en Render:
echo    - SECRET_KEY: Genera una clave segura
echo    - MONGO_URI: Usa la URL de la base de datos de Render
echo    - CORS_ORIGINS: Actualiza con tu dominio de Render
echo    - MAIL_USERNAME/MAIL_PASSWORD: Configura email de producción
echo.
echo 🚀 Para desplegar en Render:
echo    1. Sube el código a GitHub
echo    2. Conecta el repositorio en Render
echo    3. Configura las variables de entorno
echo    4. Despliega
echo.
pause
