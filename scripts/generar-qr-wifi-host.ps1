# Script wrapper para ejecutar generar-qr-wifi.py desde el host
# Detecta la red WiFi localmente y luego ejecuta el script en Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DETECTANDO RED WIFI ACTUAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detectar red WiFi
$redWifi = ""
try {
    $output = netsh wlan show interfaces 2>&1 | Out-String
    $lines = $output -split "`n"
    
    foreach ($line in $lines) {
        if ($line -match "^\s*SSID\s*:\s*(.+)$" -and $line -notmatch "BSSID") {
            $redWifi = $matches[1].Trim()
            if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
                Write-Host "Red WiFi detectada: $redWifi" -ForegroundColor Green
                break
            }
        }
    }
    
    # Si no se encontró con el patrón anterior, intentar método alternativo
    if (-not $redWifi) {
        $result = netsh wlan show interfaces | Select-String -Pattern "^\s*SSID\s*:" | Select-Object -First 1
        if ($result) {
            $parts = ($result -split ":")
            if ($parts.Length -gt 1) {
                $redWifi = $parts[-1].Trim()
                if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
                    Write-Host "Red WiFi detectada: $redWifi" -ForegroundColor Green
                }
            }
        }
    }
} catch {
    Write-Host "No se pudo detectar la red WiFi" -ForegroundColor Yellow
}

# Si se detectó una red, actualizar el .env primero
if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
    Write-Host ""
    Write-Host "Actualizando .env con red WiFi: $redWifi" -ForegroundColor Cyan
    
    $envLines = Get-Content ".env"
    $updated = $false
    $newLines = @()
    
    foreach ($line in $envLines) {
        if ($line -match "^\s*WIFI_SSID\s*=") {
            $newLines += "WIFI_SSID=$redWifi"
            $updated = $true
        } else {
            $newLines += $line
        }
    }
    
    if ($updated) {
        $newLines | Set-Content ".env"
        Write-Host "✅ .env actualizado automáticamente" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No se encontró WIFI_SSID en .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  No se detectó red WiFi, usando la del .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EJECUTANDO SCRIPT EN DOCKER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ejecutar el script en Docker
docker compose exec backend python /scripts/generar-qr-wifi.py

