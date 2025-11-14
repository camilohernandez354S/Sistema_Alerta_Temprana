# Script para actualizar configuración de red en .env
# Detecta IP y red WiFi automáticamente
# Actualiza el .env en la raíz del proyecto

# Obtener la ruta del script y la raíz del proyecto
$scriptPath = $PSScriptRoot
$projectRoot = Split-Path $scriptPath -Parent
$envFile = Join-Path $projectRoot ".env"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ACTUALIZANDO CONFIGURACION DE RED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Archivo .env: $envFile" -ForegroundColor Gray
Write-Host ""

# 1. Detectar IP de la red
Write-Host "1. Detectando IP de la red..." -ForegroundColor Yellow
$ip = ""
try {
    $ipconfig = ipconfig | Out-String
    $lines = $ipconfig -split "`n"
    
    foreach ($line in $lines) {
        if ($line -match "IPv4.*:\s*(\d+\.\d+\.\d+\.\d+)" -and $line -notmatch "172\.(1[6-9]|2[0-9]|3[0-1])") {
            $ip = $matches[1]
            if ($ip -notmatch "^172\.(1[6-9]|2[0-9]|3[0-1])" -and $ip -notmatch "^127\.") {
                Write-Host "   IP detectada: $ip" -ForegroundColor Green
                break
            }
        }
    }
} catch {
    Write-Host "   No se pudo detectar IP" -ForegroundColor Yellow
}

# 2. Detectar red WiFi
Write-Host ""
Write-Host "2. Detectando red WiFi..." -ForegroundColor Yellow
$redWifi = ""

# Método 1: Usar Get-NetConnectionProfile (más confiable en Windows)
try {
    $profile = Get-NetConnectionProfile -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*WLAN*" } | Select-Object -First 1
    if ($profile -and $profile.Name) {
        $redWifi = $profile.Name.Trim()
        if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
            Write-Host "   Red WiFi detectada: $redWifi" -ForegroundColor Green
        }
    }
} catch {
    # Continuar con otros métodos
}

# Método 2: netsh wlan show interfaces (si el método 1 falló)
if (-not $redWifi) {
    try {
        $output = netsh wlan show interfaces 2>&1 | Out-String
        if ($output) {
            $lines = $output -split "`r?`n"
            
            foreach ($line in $lines) {
                # Buscar línea que contenga SSID pero no BSSID ni Nombre
                if ($line -match "SSID" -and $line -notmatch "BSSID" -and $line -notmatch "Nombre") {
                    # Extraer el SSID después de los dos puntos
                    if ($line -match ":\s*(.+)$") {
                        $redWifi = $matches[1].Trim()
                        if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
                            Write-Host "   Red WiFi detectada: $redWifi" -ForegroundColor Green
                            break
                        }
                    }
                }
            }
        }
    } catch {
        # Continuar
    }
}

# Método 3: Intentar con Select-String como fallback
if (-not $redWifi) {
    try {
        $result = netsh wlan show interfaces 2>&1 | Select-String -Pattern "^\s*SSID\s*:" | Where-Object { $_ -notmatch "BSSID" } | Select-Object -First 1
        if ($result) {
            $lineStr = $result.ToString()
            $parts = $lineStr -split ":"
            if ($parts.Length -gt 1) {
                $redWifi = $parts[-1].Trim()
                if ($redWifi -and $redWifi -ne "" -and $redWifi -ne "none") {
                    Write-Host "   Red WiFi detectada: $redWifi" -ForegroundColor Green
                }
            }
        }
    } catch {
        Write-Host "   No se pudo detectar red WiFi" -ForegroundColor Yellow
        Write-Host "   (Puede requerir permisos de administrador)" -ForegroundColor Yellow
    }
}

# 3. Intentar obtener contraseña WiFi de perfiles guardados
$wifiPassword = ""
if ($redWifi) {
    Write-Host ""
    Write-Host "3. Obteniendo contraseña WiFi..." -ForegroundColor Yellow
    try {
        # Intentar obtener la contraseña del perfil guardado (requiere permisos de administrador)
        $profileOutput = netsh wlan show profile name="$redWifi" key=clear 2>&1 | Out-String
        if ($profileOutput -match "Contenido de la clave\s*:\s*(.+)" -or $profileOutput -match "Key Content\s*:\s*(.+)") {
            $wifiPassword = $matches[1].Trim()
            if ($wifiPassword -and $wifiPassword -ne "") {
                Write-Host "   Contrasena WiFi obtenida del perfil guardado" -ForegroundColor Green
            }
        }
    } catch {
        # No se pudo obtener, continuar
    }
    
    if (-not $wifiPassword) {
        Write-Host "   No se pudo obtener la contrasena automaticamente" -ForegroundColor Yellow
        Write-Host "   (Requiere permisos de administrador o perfil no guardado)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   IMPORTANTE: Si cambiaste de red WiFi, actualiza WIFI_PASSWORD en el .env" -ForegroundColor Red
        Write-Host "   Red actual: $redWifi" -ForegroundColor Cyan
    }
}

# 4. Actualizar .env
Write-Host ""
Write-Host "4. Actualizando archivo .env..." -ForegroundColor Yellow
Write-Host "   Ruta: $envFile" -ForegroundColor Gray

# Verificar que el archivo existe
if (-not (Test-Path $envFile)) {
    Write-Host "   ERROR: No se encontro el archivo .env en: $envFile" -ForegroundColor Red
    exit 1
}

$envLines = Get-Content $envFile
$newLines = @()
$updated = $false
$wifiSSIDUpdated = $false

foreach ($line in $envLines) {
    if ($ip -and $line -match "^\s*SERVER_IP\s*=") {
        $newLines += "SERVER_IP=$ip"
        $updated = $true
        Write-Host "   SERVER_IP actualizado: $ip" -ForegroundColor Green
    }
    elseif ($ip -and $line -match "^\s*FLASK_SERVER_URL\s*=") {
        $newLines += "FLASK_SERVER_URL=http://${ip}:5000"
        $updated = $true
        Write-Host "   FLASK_SERVER_URL actualizado: http://${ip}:5000" -ForegroundColor Green
    }
    elseif ($redWifi -and $line -match "^\s*WIFI_SSID\s*=") {
        $newLines += "WIFI_SSID=$redWifi"
        $updated = $true
        $wifiSSIDUpdated = $true
        Write-Host "   WIFI_SSID actualizado: $redWifi" -ForegroundColor Green
    }
    elseif ($wifiPassword -and $line -match "^\s*WIFI_PASSWORD\s*=") {
        $newLines += "WIFI_PASSWORD=$wifiPassword"
        $updated = $true
        Write-Host "   WIFI_PASSWORD actualizado" -ForegroundColor Green
    }
    else {
        $newLines += $line
    }
}

# Si se actualizó el SSID pero no la contraseña, mostrar advertencia
if ($wifiSSIDUpdated -and -not $wifiPassword) {
    Write-Host ""
    Write-Host "   ADVERTENCIA: Se actualizo WIFI_SSID pero no WIFI_PASSWORD" -ForegroundColor Red
    Write-Host "   Verifica que la contrasena en .env sea correcta para: $redWifi" -ForegroundColor Yellow
}

if ($updated) {
    $newLines | Set-Content $envFile -Encoding UTF8
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "CONFIGURACION ACTUALIZADA" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ejecuta 'docker compose up -d --build' para aplicar los cambios." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "No se realizaron cambios en el .env" -ForegroundColor Yellow
}

Write-Host ""

