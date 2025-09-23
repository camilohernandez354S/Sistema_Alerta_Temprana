#!/bin/bash

# Script de inicio para el Sistema de Alerta Temprana
# Soporta desarrollo y producción

echo "🚀 Sistema de Alerta Temprana - Iniciando..."

# Verificar si estamos en producción o desarrollo
if [ "$FLASK_ENV" = "production" ]; then
    echo "📦 Modo: Producción"
    echo "🔧 Iniciando con Gunicorn..."
    gunicorn --config gunicorn.conf.py wsgi:application
else
    echo "🛠️ Modo: Desarrollo"
    echo "🔧 Iniciando servidor de desarrollo..."
    python run.py
fi
