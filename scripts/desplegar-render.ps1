# Script para desplegar en Render desde la terminal
# Requiere: Render API Key configurada en variable de entorno RENDER_API_KEY

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$All,
    [string]$ApiKey = $env:RENDER_API_KEY
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Despliegue en Render" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar API Key
if (-not $ApiKey) {
    Write-Host "Error: RENDER_API_KEY no esta configurada" -ForegroundColor Red
    Write-Host ""
    Write-Host "Configura tu API Key:" -ForegroundColor Yellow
    Write-Host "  1. Ve a https://dashboard.render.com/account/api-keys" -ForegroundColor White
    Write-Host "  2. Crea una nueva API Key" -ForegroundColor White
    Write-Host "  3. Ejecuta: `$env:RENDER_API_KEY='tu_api_key'`" -ForegroundColor White
    Write-Host "  4. O pasa la key como parametro: -ApiKey 'tu_key'" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Headers para la API de Render
$headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}

# Función para obtener el servicio ID por nombre
function Get-ServiceId {
    param([string]$ServiceName)
    
    $url = "https://api.render.com/v1/services"
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
        $service = $response | Where-Object { $_.service.name -eq $ServiceName }
        if ($service) {
            return $service.service.id
        }
        return $null
    } catch {
        Write-Host "Error al obtener servicios: $_" -ForegroundColor Red
        return $null
    }
}

# Función para desplegar un servicio
function Deploy-Service {
    param(
        [string]$ServiceName,
        [string]$ServiceId
    )
    
    Write-Host "Desplegando $ServiceName..." -ForegroundColor Yellow
    
    $url = "https://api.render.com/v1/services/$ServiceId/deploys"
    $body = @{
        clearCache = $true
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
        Write-Host "Despliegue iniciado para $ServiceName" -ForegroundColor Green
        Write-Host "   Deploy ID: $($response.deploy.id)" -ForegroundColor Gray
        Write-Host "   Estado: $($response.deploy.status)" -ForegroundColor Gray
        Write-Host "   Ver progreso: https://dashboard.render.com/web/$ServiceId" -ForegroundColor Cyan
        return $true
    } catch {
        Write-Host "Error al desplegar $ServiceName : $_" -ForegroundColor Red
        return $false
    }
}

# Determinar qué desplegar
$deployBackend = $Backend -or $All
$deployFrontend = $Frontend -or $All

if (-not $deployBackend -and -not $deployFrontend) {
    Write-Host "Selecciona que desplegar:" -ForegroundColor Yellow
    Write-Host "  -Backend    : Desplegar solo backend" -ForegroundColor White
    Write-Host "  -Frontend   : Desplegar solo frontend" -ForegroundColor White
    Write-Host "  -All        : Desplegar ambos" -ForegroundColor White
    Write-Host ""
    Write-Host "Ejemplo: .\scripts\desplegar-render.ps1 -All" -ForegroundColor Cyan
    exit 0
}

# Verificar que estamos en el directorio raíz
if (-not (Test-Path "render.yaml")) {
    Write-Host "Error: render.yaml no encontrado" -ForegroundColor Red
    Write-Host "Ejecuta este script desde la raiz del proyecto" -ForegroundColor Yellow
    exit 1
}

# Verificar que hay cambios en Git
Write-Host "Verificando cambios en Git..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Advertencia: Hay cambios sin commitear" -ForegroundColor Yellow
    Write-Host "Es recomendable hacer commit y push antes de desplegar" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "¿Continuar de todas formas? (s/n)"
    if ($continue -ne "s") {
        exit 0
    }
}

# Desplegar servicios
$success = $true

if ($deployBackend) {
    $backendId = Get-ServiceId -ServiceName "sat-backend"
    if ($backendId) {
        $result = Deploy-Service -ServiceName "sat-backend" -ServiceId $backendId
        if (-not $result) { $success = $false }
    } else {
        Write-Host "Error: Servicio 'sat-backend' no encontrado en Render" -ForegroundColor Red
        Write-Host "Asegurate de haber creado el servicio desde render.yaml" -ForegroundColor Yellow
        $success = $false
    }
    Write-Host ""
}

if ($deployFrontend) {
    $frontendId = Get-ServiceId -ServiceName "sat-frontend"
    if ($frontendId) {
        $result = Deploy-Service -ServiceName "sat-frontend" -ServiceId $frontendId
        if (-not $result) { $success = $false }
    } else {
        Write-Host "Error: Servicio 'sat-frontend' no encontrado en Render" -ForegroundColor Red
        Write-Host "Asegurate de haber creado el servicio desde render.yaml" -ForegroundColor Yellow
        $success = $false
    }
    Write-Host ""
}

if ($success) {
    Write-Host "Despliegue completado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Siguiente paso:" -ForegroundColor Cyan
    Write-Host "  1. Ve a https://dashboard.render.com para ver el progreso" -ForegroundColor White
    Write-Host "  2. Espera a que los servicios se activen" -ForegroundColor White
    Write-Host "  3. Verifica que todo funcione correctamente" -ForegroundColor White
} else {
    Write-Host "Hubo errores durante el despliegue" -ForegroundColor Red
    exit 1
}

