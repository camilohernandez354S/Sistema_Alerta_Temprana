# Script auxiliar para detectar la red WiFi actual en Windows
# Se ejecuta desde el host

try {
    $result = netsh wlan show interfaces | Select-String -Pattern "SSID" | Select-Object -First 1
    
    if ($result) {
        $ssid = ($result -split ":")[1].Trim()
        if ($ssid -and $ssid -ne "" -and $ssid -ne "none") {
            Write-Output $ssid
            exit 0
        }
    }
    
    exit 1
} catch {
    exit 1
}

