# Script para hacer push de cambios a GitHub y actualizar Vercel

Write-Host "Verificando estado del repositorio..." -ForegroundColor Cyan
git status

Write-Host "`nAgregando cambios al staging area..." -ForegroundColor Cyan
git add src/views/Coworking.vue
git add src/router/index.js
git add vercel.json

Write-Host "`nCreando commit..." -ForegroundColor Cyan
git commit -m "feat: actualizar Coworking y configuración para Vercel"

Write-Host "`nHaciendo push a eltorete/main..." -ForegroundColor Cyan
git push eltorete main

Write-Host "`n✅ Cambios enviados exitosamente!" -ForegroundColor Green
Write-Host "Vercel debería detectar los cambios y hacer un nuevo despliegue automáticamente." -ForegroundColor Yellow


