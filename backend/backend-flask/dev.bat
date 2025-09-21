@echo off
REM Script de desarrollo para Windows - Sistema Arduino Nivel Agua

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="install" goto install
if "%1"=="run" goto run
if "%1"=="test" goto test
if "%1"=="test-cov" goto test_cov
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="clean" goto clean
goto help

:help
echo.
echo 🛠️ Script de Desarrollo - Sistema Arduino Nivel Agua (Windows)
echo.
echo Comandos disponibles:
echo   dev.bat setup      Configurar entorno de desarrollo
echo   dev.bat install    Instalar dependencias
echo   dev.bat run        Ejecutar aplicacion en desarrollo
echo   dev.bat test       Ejecutar tests
echo   dev.bat test-cov   Ejecutar tests con cobertura
echo   dev.bat lint       Verificar codigo
echo   dev.bat format     Formatear codigo
echo   dev.bat clean      Limpiar archivos temporales
echo   dev.bat help       Mostrar esta ayuda
echo.
goto end

:setup
echo ⚙️ Configurando entorno de desarrollo...
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
echo ✅ Configuracion completada
goto end

:install
echo 📦 Instalando dependencias...
pip install -r requirements.txt
echo ✅ Dependencias instaladas
goto end

:run
echo 🚀 Iniciando aplicacion en modo desarrollo...
set FLASK_ENV=development
set LOG_LEVEL=DEBUG
python run.py
goto end

:test
echo 🧪 Ejecutando tests...
pytest -v --tb=short
goto end

:test_cov
echo 📊 Ejecutando tests con cobertura...
pytest --cov=app --cov-report=html --cov-report=term
goto end

:lint
echo 🔍 Verificando codigo...
flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
echo ✅ Verificacion completada
goto end

:format
echo ✨ Formateando codigo...
black app/ --line-length=88
isort app/ --profile black
echo ✅ Formateo completado
goto end

:clean
echo 🧹 Limpiando archivos temporales...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
del /s /q *.pyo >nul 2>&1
if exist .coverage del .coverage
if exist htmlcov rmdir /s /q htmlcov
if exist .pytest_cache rmdir /s /q .pytest_cache
echo ✅ Limpieza completada
goto end

:end
