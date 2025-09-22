# Makefile para el backend Flask - Sistema Arduino Nivel Agua

.PHONY: help install setup run test test-cov lint format clean docker-build docker-run venv dev ci db-setup logs quick-test fix all

# Variables
PYTHON = python3
PIP = pip3
VENV = venv
FLASK_APP = run.py

help: ## Mostrar esta ayuda
	@echo "🚀 Sistema Arduino Nivel Agua - Backend Flask"
	@echo ""
	@echo "Comandos disponibles:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Configuración e instalación
install: ## Instalar dependencias
	@echo "📦 Instalando dependencias..."
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencias instaladas"

setup: ## Configurar entorno de desarrollo
	@echo "⚙️ Configurando entorno de desarrollo..."
	@mkdir -p logs
	@if [ ! -f .env ]; then \
		if [ -f env.example ]; then \
			cp env.example .env; \
			echo "📝 Archivo .env creado desde env.example"; \
		else \
			echo "⚠️ env.example no encontrado"; \
		fi \
	else \
		echo "📝 Archivo .env ya existe"; \
	fi
	@echo "✅ Entorno configurado"

venv: ## Crear entorno virtual
	@echo "🐍 Creando entorno virtual..."
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Entorno virtual creado en ./$(VENV)"
	@echo "💡 Activar con: source $(VENV)/bin/activate (Linux/Mac) o $(VENV)\\Scripts\\activate (Windows)"

# Ejecución
run: ## Ejecutar aplicación en desarrollo
	@echo "🚀 Iniciando aplicación en modo desarrollo..."
	FLASK_ENV=development LOG_LEVEL=DEBUG $(PYTHON) $(FLASK_APP)

run-prod: ## Ejecutar aplicación en producción
	@echo "🏭 Iniciando aplicación en modo producción..."
	FLASK_ENV=production $(PYTHON) $(FLASK_APP)

run-test: ## Ejecutar aplicación en modo test
	@echo "🧪 Iniciando aplicación en modo test..."
	FLASK_ENV=testing LOG_LEVEL=DEBUG $(PYTHON) $(FLASK_APP)

# Testing
test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	pytest -v --tb=short

test-cov: ## Ejecutar tests con cobertura
	@echo "📊 Ejecutando tests con cobertura..."
	pytest --cov=app --cov-report=html --cov-report=term-missing

quick-test: ## Tests rápidos (sin cobertura)
	@echo "⚡ Ejecutando tests rápidos..."
	pytest -x --tb=short

test-watch: ## Ejecutar tests en modo watch
	@echo "👁️ Ejecutando tests en modo watch..."
	pytest-watch

# Calidad de código
lint: ## Ejecutar linting
	@echo "🔍 Ejecutando linting..."
	flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "✅ Linting completado"

format: ## Formatear código
	@echo "✨ Formateando código..."
	black app/ --line-length=88
	isort app/ --profile black
	@echo "✅ Formateo completado"

format-check: ## Verificar formato sin aplicar cambios
	@echo "🔍 Verificando formato..."
	black app/ --check --line-length=88
	isort app/ --check-only --profile black

fix: format lint ## Formatear y verificar código
	@echo "🔧 Código formateado y verificado"

# Limpieza
clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .coverage htmlcov/ .pytest_cache/ dist/ build/
	@echo "✅ Limpieza completada"

clean-logs: ## Limpiar archivos de log
	@echo "🗑️ Limpiando logs..."
	@rm -rf logs/*.log*
	@echo "✅ Logs limpiados"

# Docker
docker-build: ## Construir imagen Docker
	@echo "🐳 Construyendo imagen Docker..."
	docker build -t sensor-api:latest .
	@echo "✅ Imagen Docker construida"

docker-run: ## Ejecutar contenedor Docker
	@echo "🐳 Ejecutando contenedor Docker..."
	docker run -p 5000:5000 --env-file .env sensor-api:latest

docker-dev: ## Ejecutar contenedor Docker en modo desarrollo
	@echo "🐳 Ejecutando contenedor Docker en desarrollo..."
	docker run -p 5000:5000 -v $(PWD):/app --env-file .env sensor-api:latest

# Base de datos
db-setup: ## Configurar y verificar base de datos
	@echo "🗄️ Verificando conexión a MongoDB..."
	$(PYTHON) -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/')); client.server_info(); print('✅ MongoDB conectado correctamente')"

db-reset: ## Resetear base de datos de desarrollo (¡CUIDADO!)
	@echo "⚠️ Reseteando base de datos de desarrollo..."
	@read -p "¿Estás seguro? Esto eliminará todos los datos [y/N]: " confirm && [ "$$confirm" = "y" ]
	$(PYTHON) -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGO_URI')); client.drop_database(os.getenv('MONGO_DB')); print('🗑️ Base de datos reseteada')"

# Logs y monitoreo
logs: ## Ver logs de la aplicación
	@echo "📋 Mostrando logs de la aplicación..."
	@if [ -f logs/app.log ]; then \
		tail -f logs/app.log; \
	else \
		echo "📝 No hay logs disponibles. Ejecuta la aplicación primero."; \
	fi

logs-error: ## Ver solo logs de error
	@echo "🚨 Mostrando logs de error..."
	@if [ -f logs/app.log ]; then \
		grep -i "error\|exception\|traceback" logs/app.log | tail -20; \
	else \
		echo "📝 No hay logs disponibles."; \
	fi

# Workflows completos
dev: setup install ## Configurar y preparar entorno de desarrollo completo
	@echo "🎯 Entorno de desarrollo listo"
	@echo "💡 Ejecuta 'make run' para iniciar la aplicación"

ci: clean format-check lint test ## Pipeline de CI (clean, format-check, lint, test)
	@echo "✅ Pipeline de CI completado exitosamente"

release: clean lint test ## Preparar release (limpiar, verificar, tests)
	@echo "🚀 Release preparado exitosamente"

all: clean install test lint format ## Ejecutar pipeline completo
	@echo "🏆 Pipeline completo ejecutado exitosamente"

# Desarrollo y debugging
debug: ## Ejecutar aplicación con debugger
	@echo "🐛 Iniciando aplicación con debugger..."
	FLASK_ENV=development LOG_LEVEL=DEBUG FLASK_DEBUG=1 $(PYTHON) $(FLASK_APP)

shell: ## Abrir shell interactivo de Flask
	@echo "🐚 Abriendo shell de Flask..."
	FLASK_ENV=development $(PYTHON) -c "from app import create_app; app = create_app(); app.app_context().push(); print('Shell de Flask iniciado. Variable app disponible.')"

requirements: ## Actualizar requirements.txt
	@echo "📋 Actualizando requirements.txt..."
	$(PIP) freeze > requirements.txt
	@echo "✅ requirements.txt actualizado"

# Información del sistema
info: ## Mostrar información del sistema
	@echo "📊 Información del Sistema:"
	@echo "Python: $$(python --version)"
	@echo "Pip: $$(pip --version)"
	@echo "Sistema: $$(uname -s)"
	@echo "Directorio: $$(pwd)"
	@echo "Archivos .env: $$(if [ -f .env ]; then echo 'Existe'; else echo 'No existe'; fi)"
	@echo "MongoDB: $$(if command -v mongod > /dev/null; then echo 'Instalado'; else echo 'No encontrado'; fi)"

status: ## Verificar estado del proyecto
	@echo "🔍 Estado del Proyecto:"
	@echo "Dependencias: $$(if [ -d venv ] || pip list > /dev/null 2>&1; then echo 'OK'; else echo 'Faltan'; fi)"
	@echo "Configuración: $$(if [ -f .env ]; then echo 'OK'; else echo 'Falta .env'; fi)"
	@echo "Logs: $$(if [ -d logs ]; then echo 'OK'; else echo 'Directorio falta'; fi)"
	@echo "Tests: $$(if [ -d tests ]; then echo 'OK'; else echo 'Directorio falta'; fi)"

# Ayuda específica
help-docker: ## Ayuda para comandos Docker
	@echo "🐳 Comandos Docker disponibles:"
	@echo "  make docker-build    - Construir imagen"
	@echo "  make docker-run      - Ejecutar contenedor"
	@echo "  make docker-dev      - Ejecutar en modo desarrollo"

help-db: ## Ayuda para comandos de base de datos
	@echo "🗄️ Comandos de base de datos disponibles:"
	@echo "  make db-setup        - Verificar conexión MongoDB"
	@echo "  make db-reset        - Resetear base de datos (¡CUIDADO!)"
