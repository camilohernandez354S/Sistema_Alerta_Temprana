# Script para verificar la configuración del Arduino desde .env
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verificacion de Configuracion Arduino" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que .env existe
if (-not (Test-Path ".env")) {
    Write-Host "Error: No se encontro el archivo .env" -ForegroundColor Red
    Write-Host "Copia config/example.env a .env y configuralo" -ForegroundColor Yellow
    exit 1
}

Write-Host "Leyendo configuracion desde .env..." -ForegroundColor Yellow
Write-Host ""

# Cargar .env
$envContent = Get-Content ".env" | Where-Object { $_ -match "^\s*[^#]" -and $_ -match "=" }

$config = @{}
foreach ($line in $envContent) {
    if ($line -match "^([^=]+)=(.*)$") {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $config[$key] = $value
    }
}

# Mostrar configuración
Write-Host "CONFIGURACION DE RED (desde .env)" -ForegroundColor Green
Write-Host "-" * 50 -ForegroundColor Gray
Write-Host ""

# IP y Puerto del Servidor
$serverIp = $config['SERVER_IP']
$serverPort = $config['SERVER_PORT']
$flaskUrl = $config['FLASK_SERVER_URL']

if (-not $flaskUrl -and $serverIp -and $serverPort) {
    $flaskUrl = "http://${serverIp}:${serverPort}"
}

Write-Host "Servidor Flask:" -ForegroundColor Cyan
Write-Host "   IP:              $($serverIp ?? '(no configurado)')" -ForegroundColor White
Write-Host "   Puerto:           $($serverPort ?? '(no configurado)')" -ForegroundColor White
Write-Host "   URL Completa:     $($flaskUrl ?? '(no configurado)')" -ForegroundColor White
Write-Host ""

# WiFi
$wifiSsid = $config['WIFI_SSID']
$wifiPassword = $config['WIFI_PASSWORD']

Write-Host "Credenciales WiFi (para Arduino):" -ForegroundColor Cyan
Write-Host "   SSID:             $($wifiSsid ?? '(no configurado)')" -ForegroundColor White
Write-Host "   Password:         $(if ($wifiPassword) { '*' * $wifiPassword.Length } else { '(no configurado)' })" -ForegroundColor White
Write-Host ""

# Validar
$errores = @()
if (-not $wifiSsid) {
    $errores += "WIFI_SSID no esta configurado"
}
if (-not $serverIp -and -not $flaskUrl) {
    $errores += "SERVER_IP o FLASK_SERVER_URL no esta configurado"
}

if ($errores.Count -gt 0) {
    Write-Host "ADVERTENCIAS:" -ForegroundColor Yellow
    foreach ($error in $errores) {
        Write-Host "   - $error" -ForegroundColor Yellow
    }
    Write-Host ""
} else {
    Write-Host "Configuracion valida!" -ForegroundColor Green
    Write-Host ""
}

# Generar configuración WiFi
Write-Host "Generando wifi_config.h..." -ForegroundColor Yellow
Write-Host ""

$pythonScript = "backend\arduino\generar_config_wifi.py"
if (Test-Path $pythonScript) {
    python $pythonScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Resumen:" -ForegroundColor Green
        Write-Host "   El Arduino usara:" -ForegroundColor White
        Write-Host "   - Red WiFi: $wifiSsid" -ForegroundColor White
        Write-Host "   - Servidor: $flaskUrl" -ForegroundColor White
        Write-Host ""
        Write-Host "Siguiente paso:" -ForegroundColor Cyan
        Write-Host "   1. Abre backend/arduino/nivel_agua_wifi.ino en Arduino IDE" -ForegroundColor White
        Write-Host "   2. Verifica que wifi_config.h tenga la configuracion correcta" -ForegroundColor White
        Write-Host "   3. Sube el codigo al ESP8266/ESP32" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "Error al generar wifi_config.h" -ForegroundColor Red
    }
} else {
    Write-Host "Advertencia: No se encontro el script generar_config_wifi.py" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Presiona Enter para continuar"

