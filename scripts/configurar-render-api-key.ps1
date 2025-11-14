# Script para configurar la API Key de Render

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuracion de API Key de Render" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Para desplegar en Render desde la terminal, necesitas una API Key." -ForegroundColor Yellow
Write-Host ""

Write-Host "Pasos:" -ForegroundColor Cyan
Write-Host "  1. Ve a https://dashboard.render.com/account/api-keys" -ForegroundColor White
Write-Host "  2. Inicia sesion en tu cuenta de Render" -ForegroundColor White
Write-Host "  3. Crea una nueva API Key" -ForegroundColor White
Write-Host "  4. Copia la key generada" -ForegroundColor White
Write-Host ""

$apiKey = Read-Host "Pega tu API Key aqui"

if ($apiKey) {
    # Configurar para la sesion actual
    $env:RENDER_API_KEY = $apiKey
    
    # Guardar en perfil de PowerShell (opcional)
    $profilePath = $PROFILE
    $saveToProfile = Read-Host "¿Guardar en el perfil de PowerShell? (s/n)"
    
    if ($saveToProfile -eq "s") {
        if (-not (Test-Path $profilePath)) {
            New-Item -Path $profilePath -ItemType File -Force | Out-Null
        }
        
        $content = Get-Content $profilePath -ErrorAction SilentlyContinue
        if ($content -notmatch "RENDER_API_KEY") {
            Add-Content -Path $profilePath -Value "`$env:RENDER_API_KEY = '$apiKey'"
            Write-Host "API Key guardada en perfil de PowerShell" -ForegroundColor Green
        } else {
            Write-Host "API Key ya existe en el perfil. Actualizala manualmente si es necesario." -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "API Key configurada para esta sesion!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ahora puedes desplegar con:" -ForegroundColor Cyan
    Write-Host "  .\scripts\desplegar-render.ps1 -All" -ForegroundColor White
} else {
    Write-Host "No se proporciono API Key" -ForegroundColor Red
}

Write-Host ""
Read-Host "Presiona Enter para continuar"

