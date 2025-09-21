@echo off
echo 🔧 Configurando entorno Flask - Sistema Arduino
echo.

REM Paso 1: Limpiar instalaciones conflictivas
echo 📦 Paso 1: Limpiando dependencias conflictivas...
pip uninstall bson -y 2>nul
pip uninstall pymongo -y 2>nul

REM Paso 2: Instalar pymongo (que incluye bson)
echo 📦 Paso 2: Instalando pymongo...
pip install pymongo==4.6.1

REM Paso 3: Instalar el resto de dependencias
echo 📦 Paso 3: Instalando dependencias principales...
pip install flask==3.1.1
pip install flask-cors==5.0.1
pip install python-dotenv==1.1.0
pip install pydantic==2.11.4

echo 📦 Paso 4: Instalando dependencias de ML...
pip install numpy==2.2.5
pip install pandas==2.2.3
pip install scikit-learn==1.6.1
pip install scipy==1.15.3

echo 📦 Paso 5: Instalando utilidades...
pip install requests==2.32.3

echo 📦 Paso 6: Instalando herramientas de desarrollo...
pip install pytest==8.3.4
pip install pytest-flask==1.3.0
pip install pytest-cov==6.0.0
pip install flake8==7.1.1
pip install black==24.10.0
pip install isort==5.13.2

REM Paso 7: Configurar entorno
echo ⚙️ Paso 7: Configurando entorno...
if not exist logs mkdir logs
if not exist .env (
    if exist env.example (
        copy env.example .env
        echo 📝 Archivo .env creado desde env.example
    ) else (
        echo ⚠️ env.example no encontrado
    )
) else (
    echo 📝 Archivo .env ya existe
)

echo.
echo ✅ Configuración completada!
echo.
echo 🚀 Para ejecutar la aplicación:
echo    python run.py
echo.
echo 🧪 Para ejecutar tests:
echo    pytest
echo.
pause
