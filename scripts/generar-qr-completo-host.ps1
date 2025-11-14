# Script completo para actualizar configuración y generar QR codes
# 1. Detecta IP y red WiFi
# 2. Actualiza el .env
# 3. Genera los QR codes en Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GENERANDO QR CODES Y ACTUALIZANDO CONFIG" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ejecutar script de actualización de configuración
Write-Host "Paso 1: Actualizando configuracion de red..." -ForegroundColor Yellow
Write-Host ""
& "$PSScriptRoot\actualizar-config-red.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Paso 2: Generando QR codes en Docker..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Generar QR de WiFi
Write-Host "Generando QR de WiFi..." -ForegroundColor Yellow
docker compose exec backend python /scripts/generar-qr-wifi.py

Write-Host ""
Write-Host "Generando QR de URL..." -ForegroundColor Yellow
docker compose exec backend python /scripts/generar-qr-url.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROCESO COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "QR codes generados en:" -ForegroundColor Green
Write-Host "   - qr_codes/wifi/qr-wifi-*.png" -ForegroundColor White
Write-Host "   - qr_codes/url/qr-url-*.png" -ForegroundColor White
Write-Host ""
Write-Host "El archivo .env ha sido actualizado." -ForegroundColor Green
Write-Host ""
Write-Host "Paso 3: Reiniciando contenedores..." -ForegroundColor Yellow
Write-Host ""
docker compose up -d --build

Write-Host ""
Write-Host "✅ Proceso completado" -ForegroundColor Green
Write-Host ""
