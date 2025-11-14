# Script para limpiar node_modules y reinstalar dependencias
# Ejecutar desde la carpeta frontend: .\clean-node-modules.ps1

Write-Host "🧹 Limpiando node_modules..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force node_modules
    Write-Host "✅ node_modules eliminado" -ForegroundColor Green
} else {
    Write-Host "⚠️  node_modules no existe" -ForegroundColor Yellow
}

if (Test-Path "package-lock.json") {
    Remove-Item -Force package-lock.json
    Write-Host "✅ package-lock.json eliminado" -ForegroundColor Green
}

Write-Host "📦 Reinstalando dependencias..." -ForegroundColor Yellow
npm install

Write-Host "✅ Proceso completado" -ForegroundColor Green

