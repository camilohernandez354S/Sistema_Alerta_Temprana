# Script para configurar Arduino para conexión remota
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuracion Arduino para Produccion" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Solicitar URL del backend remoto
$backendUrl = Read-Host "Ingresa la URL del backend remoto (ej: https://sat-backend.onrender.com)"

if (-not $backendUrl) {
    Write-Host "Error: Debes ingresar una URL valida" -ForegroundColor Red
    exit 1
}

# Validar formato de URL
if ($backendUrl -notmatch "^https?://") {
    Write-Host "Advertencia: La URL deberia comenzar con http:// o https://" -ForegroundColor Yellow
    $confirm = Read-Host "Continuar de todas formas? (s/n)"
    if ($confirm -ne "s") {
        exit 1
    }
}

Write-Host ""
Write-Host "Actualizando .env..." -ForegroundColor Yellow

# Leer .env actual
$envPath = ".env"
if (-not (Test-Path $envPath)) {
    Write-Host "Error: No se encontro el archivo .env" -ForegroundColor Red
    Write-Host "Copia config/example.env a .env primero" -ForegroundColor Yellow
    exit 1
}

# Leer contenido actual
$envContent = Get-Content $envPath -Raw

# Actualizar FLASK_SERVER_URL
if ($envContent -match "FLASK_SERVER_URL=.*") {
    $envContent = $envContent -replace "FLASK_SERVER_URL=.*", "FLASK_SERVER_URL=$backendUrl"
} else {
    $envContent += "`nFLASK_SERVER_URL=$backendUrl"
}

# Guardar .env actualizado
Set-Content -Path $envPath -Value $envContent -NoNewline

Write-Host "✅ .env actualizado" -ForegroundColor Green
Write-Host ""

# Generar configuración WiFi
Write-Host "Generando configuracion WiFi para Arduino..." -ForegroundColor Yellow
Write-Host ""

$pythonScript = "backend\arduino\generar_config_wifi.py"
if (Test-Path $pythonScript) {
    python $pythonScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Configuracion WiFi generada exitosamente!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Siguiente paso:" -ForegroundColor Cyan
        Write-Host "   1. Abre backend/arduino/nivel_agua_wifi.ino en Arduino IDE" -ForegroundColor White
        Write-Host "   2. Verifica que wifi_config.h tenga la URL correcta" -ForegroundColor White
        Write-Host "   3. Sube el codigo al ESP8266/ESP32" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "❌ Error al generar configuracion WiFi" -ForegroundColor Red
    }
} else {
    Write-Host "Advertencia: No se encontro el script generar_config_wifi.py" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Presiona Enter para continuar"

