# Script simplificado para actualizar .env desde Docker
# Se ejecuta desde el host cuando es llamado desde Docker

param(
    [string]$EnvFile = ".env"
)

# Detectar IP
$ip = ""
$ipconfig = ipconfig | Out-String
$lines = $ipconfig -split "`n"
foreach ($line in $lines) {
    if ($line -match "IPv4.*:\s*(\d+\.\d+\.\d+\.\d+)" -and $line -notmatch "172\.(1[6-9]|2[0-9]|3[0-1])") {
        $ip = $matches[1]
        if ($ip -notmatch "^172\.(1[6-9]|2[0-9]|3[0-1])" -and $ip -notmatch "^127\.") {
            break
        }
    }
}

# Detectar red WiFi
$redWifi = ""
try {
    $profile = Get-NetConnectionProfile -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*WLAN*" } | Select-Object -First 1
    if ($profile -and $profile.Name) {
        $redWifi = $profile.Name.Trim()
    }
} catch {}

# Obtener contraseña WiFi
$wifiPassword = ""
if ($redWifi) {
    try {
        $profileOutput = netsh wlan show profile name="$redWifi" key=clear 2>&1 | Out-String
        if ($profileOutput -match "Contenido de la clave\s*:\s*(.+)" -or $profileOutput -match "Key Content\s*:\s*(.+)") {
            $wifiPassword = $matches[1].Trim()
        }
    } catch {}
}

# Actualizar .env
if (Test-Path $EnvFile) {
    $envLines = Get-Content $EnvFile
    $newLines = @()
    $updated = $false
    
    foreach ($line in $envLines) {
        if ($ip -and $line -match "^\s*SERVER_IP\s*=") {
            $newLines += "SERVER_IP=$ip"
            $updated = $true
        }
        elseif ($ip -and $line -match "^\s*FLASK_SERVER_URL\s*=") {
            $newLines += "FLASK_SERVER_URL=http://${ip}:5000"
            $updated = $true
        }
        elseif ($redWifi -and $line -match "^\s*WIFI_SSID\s*=") {
            $newLines += "WIFI_SSID=$redWifi"
            $updated = $true
        }
        elseif ($wifiPassword -and $line -match "^\s*WIFI_PASSWORD\s*=") {
            $newLines += "WIFI_PASSWORD=$wifiPassword"
            $updated = $true
        }
        else {
            $newLines += $line
        }
    }
    
    if ($updated) {
        $newLines | Set-Content $EnvFile -Encoding UTF8
        Write-Output "OK"
    }
}

