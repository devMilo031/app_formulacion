@echo off
echo Activando entorno virtual...
if exist "..\..\..\.venv\Scripts\activate.bat" (
    call "..\..\..\..\..\..\.venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)
echo Verificando reportlab...
python -c "import reportlab" 2>nul || pip install reportlab
echo Iniciando Flask...
python app.py
pause

