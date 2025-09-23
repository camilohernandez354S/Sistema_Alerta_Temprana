@echo off
echo ==========================================
echo CONFIGURANDO ENTORNO DE DESARROLLO
echo ==========================================

REM Copiar archivo de configuración de desarrollo
copy config\development.env .env

echo.
echo ✅ Archivo .env creado para desarrollo
echo.
echo 📝 IMPORTANTE: Revisa y configura las siguientes variables:
echo    - SECRET_KEY: Cambia por una clave segura
echo    - MONGO_URI: Verifica que MongoDB esté corriendo
echo    - ARDUINO_PORT: Ajusta el puerto COM según tu Arduino
echo    - MAIL_USERNAME/MAIL_PASSWORD: Configura si usas email
echo.
echo 🚀 Para iniciar el desarrollo:
echo    docker-compose up
echo.
pause
