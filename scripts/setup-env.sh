#!/bin/bash

echo "=========================================="
echo "CONFIGURADOR DE VARIABLES DE ENTORNO"
echo "=========================================="

# Función para mostrar menú
show_menu() {
    echo ""
    echo "Selecciona el entorno a configurar:"
    echo "1) Desarrollo Local"
    echo "2) Producción (Render)"
    echo "3) Crear desde ejemplo"
    echo "4) Salir"
    echo ""
    read -p "Opción [1-4]: " choice
}

# Función para configurar desarrollo
setup_dev() {
    echo "Configurando entorno de desarrollo..."
    cp config/development.env .env
    echo "✅ Archivo .env creado para desarrollo"
    echo ""
    echo "📝 IMPORTANTE: Revisa y configura las siguientes variables:"
    echo "   - SECRET_KEY: Cambia por una clave segura"
    echo "   - MONGO_URI: Verifica que MongoDB esté corriendo"
    echo "   - ARDUINO_PORT: Ajusta el puerto COM según tu Arduino"
    echo "   - MAIL_USERNAME/MAIL_PASSWORD: Configura si usas email"
    echo ""
    echo "🚀 Para iniciar el desarrollo:"
    echo "   docker-compose up"
}

# Función para configurar producción
setup_prod() {
    echo "Configurando entorno de producción..."
    cp config/production.env .env
    echo "✅ Archivo .env creado para producción"
    echo ""
    echo "📝 IMPORTANTE: Configura estas variables en Render:"
    echo "   - SECRET_KEY: Genera una clave segura"
    echo "   - MONGO_URI: Usa la URL de la base de datos de Render"
    echo "   - CORS_ORIGINS: Actualiza con tu dominio de Render"
    echo "   - MAIL_USERNAME/MAIL_PASSWORD: Configura email de producción"
    echo ""
    echo "🚀 Para desplegar en Render:"
    echo "   1. Sube el código a GitHub"
    echo "   2. Conecta el repositorio en Render"
    echo "   3. Configura las variables de entorno"
    echo "   4. Despliega"
}

# Función para crear desde ejemplo
setup_example() {
    echo "Creando archivo .env desde ejemplo..."
    cp config/example.env .env
    echo "✅ Archivo .env creado desde ejemplo"
    echo ""
    echo "📝 Edita el archivo .env y configura todas las variables necesarias"
}

# Menú principal
while true; do
    show_menu
    case $choice in
        1)
            setup_dev
            break
            ;;
        2)
            setup_prod
            break
            ;;
        3)
            setup_example
            break
            ;;
        4)
            echo "Saliendo..."
            exit 0
            ;;
        *)
            echo "❌ Opción inválida. Intenta de nuevo."
            ;;
    esac
done
