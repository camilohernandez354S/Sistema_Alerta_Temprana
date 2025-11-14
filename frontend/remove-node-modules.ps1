# Script para eliminar node_modules (solo si usas Docker)
# Ejecutar desde la carpeta frontend: .\remove-node-modules.ps1

Write-Host "⚠️  ADVERTENCIA: Esto eliminará node_modules localmente" -ForegroundColor Yellow
Write-Host "Si solo usas Docker, está bien. Si desarrollas localmente con 'npm run dev', necesitarás ejecutar 'npm install' después." -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "¿Continuar? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Operación cancelada" -ForegroundColor Red
    exit
}

Write-Host "🧹 Eliminando node_modules..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    $size = (Get-ChildItem -Path node_modules -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "📊 Tamaño aproximado: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
    
    Remove-Item -Recurse -Force node_modules
    Write-Host "✅ node_modules eliminado exitosamente" -ForegroundColor Green
    Write-Host "💾 Espacio liberado: ~$([math]::Round($size, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "⚠️  node_modules no existe" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 Para reinstalar (si desarrollas localmente): npm install" -ForegroundColor Cyan
Write-Host "🐳 Para usar Docker: docker compose up -d --build" -ForegroundColor Cyan

