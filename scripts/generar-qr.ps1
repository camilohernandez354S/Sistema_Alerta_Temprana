# Script PowerShell para generar códigos QR
# Genera QR de WiFi y QR de URL automáticamente

Write-Host "🔲 Generando códigos QR..." -ForegroundColor Cyan
Write-Host ""

# Verificar que Python esté instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}

# Ejecutar script de generación
python scripts\generar-qr-completo.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Proceso completado" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Los QR codes están en: qr_codes\" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Error al generar QR codes" -ForegroundColor Red
    exit 1
}

