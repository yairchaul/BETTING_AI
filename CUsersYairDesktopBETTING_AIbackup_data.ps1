# Script para respaldar datos del contenedor a local
Write-Host "📦 Respaldando datos del contenedor n8n..." -ForegroundColor Green

# Crear carpeta de respaldo
$backupDir = "C:\Users\Yair\Desktop\BETTING_AI\backups\$(Get-Date -Format 'yyyy-MM-dd')"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Copiar archivos
docker cp n8n:/data/betting_ai/data/teams_database.json "$backupDir\"
docker cp n8n:/data/betting_ai/data/teams_database_complete.json "$backupDir\"
docker cp n8n:/data/betting_ai/reports "$backupDir\" -ErrorAction SilentlyContinue

Write-Host "✅ Respaldo completado en: $backupDir" -ForegroundColor Green
