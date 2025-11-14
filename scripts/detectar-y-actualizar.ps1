# Script PowerShell para detectar red WiFi, IP y actualizar .env
# Luego ejecuta docker compose up -d --build

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DETECTANDO CONFIGURACIÓN DE RED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Detectar IP
Write-Host "1. Detectando IP de la red..." -ForegroundColor Yellow
$ip = ""
try {
    $ipconfig = ipconfig | Out-String
    $lines = $ipconfig -split "`n"
    foreach ($line in $lines) {
        if ($line -match "IPv4.*:\s*(\d+\.\d+\.\d+\.\d+)" -and $line -notmatch "172\.(1[6-9]|2[0-9]|3[0-1])") {
            $ip = $matches[1]
            if ($ip -notmatch "^172\.(1[6-9]|2[0-9]|3[0-1])" -and $ip -notmatch "^127\.") {
                Write-Host "   ✅ IP detectada: $ip" -ForegroundColor Green
                break
            }
        }
    }
} catch {
    Write-Host "   ⚠️  No se pudo detectar IP" -ForegroundColor Yellow
}

# 2. Detectar red WiFi
Write-Host ""
Write-Host "2. Detectando red WiFi..." -ForegroundColor Yellow
$redWifi = ""

# Método 1: Get-NetConnectionProfile
try {
    $profile = Get-NetConnectionProfile -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*WLAN*" } | Select-Object -First 1
    if ($profile -and $profile.Name) {
        $redWifi = $profile.Name.Trim()
        if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
            Write-Host "   ✅ Red WiFi detectada: $redWifi" -ForegroundColor Green
        }
    }
} catch {}

# Método 2: netsh (fallback)
if (-not $redWifi) {
    try {
        $output = netsh wlan show interfaces 2>&1 | Out-String
        if ($output) {
            $lines = $output -split "`r?`n"
            foreach ($line in $lines) {
                if ($line -match "SSID" -and $line -notmatch "BSSID" -and $line -notmatch "Nombre") {
                    if ($line -match ":\s*(.+)$") {
                        $redWifi = $matches[1].Trim()
                        if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
                            Write-Host "   ✅ Red WiFi detectada: $redWifi" -ForegroundColor Green
                            break
                        }
                    }
                }
            }
        }
    } catch {}
}

# 3. Obtener contraseña WiFi
$wifiPassword = ""
if ($redWifi) {
    Write-Host ""
    Write-Host "3. Obteniendo contraseña WiFi..." -ForegroundColor Yellow
    try {
        $profileOutput = netsh wlan show profile name="$redWifi" key=clear 2>&1 | Out-String
        if ($profileOutput -match "Contenido de la clave\s*:\s*(.+)" -or $profileOutput -match "Key Content\s*:\s*(.+)") {
            $wifiPassword = $matches[1].Trim()
            if ($wifiPassword -and $wifiPassword -ne "") {
                Write-Host "   ✅ Contraseña WiFi obtenida" -ForegroundColor Green
            }
        }
    } catch {}
    
    if (-not $wifiPassword) {
        Write-Host "   ⚠️  No se pudo obtener la contraseña automáticamente" -ForegroundColor Yellow
    }
}

# 4. Actualizar .env
Write-Host ""
Write-Host "4. Actualizando archivo .env..." -ForegroundColor Yellow
$envFile = ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "   ❌ No se encontró el archivo .env" -ForegroundColor Red
    exit 1
}

$envLines = Get-Content $envFile
$newLines = @()
$updated = $false

foreach ($line in $envLines) {
    if ($ip -and $line -match "^\s*SERVER_IP\s*=") {
        $newLines += "SERVER_IP=$ip"
        $updated = $true
        Write-Host "   ✅ SERVER_IP actualizado: $ip" -ForegroundColor Green
    }
    elseif ($ip -and $line -match "^\s*FLASK_SERVER_URL\s*=") {
        $newLines += "FLASK_SERVER_URL=http://${ip}:5000"
        $updated = $true
        Write-Host "   ✅ FLASK_SERVER_URL actualizado: http://${ip}:5000" -ForegroundColor Green
    }
    elseif ($redWifi -and $line -match "^\s*WIFI_SSID\s*=") {
        $newLines += "WIFI_SSID=$redWifi"
        $updated = $true
        Write-Host "   ✅ WIFI_SSID actualizado: $redWifi" -ForegroundColor Green
    }
    elseif ($wifiPassword -and $line -match "^\s*WIFI_PASSWORD\s*=") {
        $newLines += "WIFI_PASSWORD=$wifiPassword"
        $updated = $true
        Write-Host "   ✅ WIFI_PASSWORD actualizado" -ForegroundColor Green
    }
    else {
        $newLines += $line
    }
}

if ($updated) {
    $newLines | Set-Content $envFile -Encoding UTF8
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "REINICIANDO CONTENEDORES" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Ejecutar docker compose up -d --build
    docker compose up -d --build
    
    Write-Host ""
    Write-Host "✅ Proceso completado" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  No se realizaron cambios en el .env" -ForegroundColor Yellow
}

