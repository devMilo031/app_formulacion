# Script para iniciar Flask con reportlab instalado
Write-Host "Verificando reportlab..." -ForegroundColor Yellow

# Intentar importar reportlab
python -c "import reportlab; print('reportlab OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalando reportlab..." -ForegroundColor Yellow
    python -m pip install reportlab
}

Write-Host "Iniciando Flask..." -ForegroundColor Green
python app.py

