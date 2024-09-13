@echo off
REM Verifica si el entorno virtual existe y lo activa
if exist ".\env\Scripts\activate.bat" (
    call .\env\Scripts\activate.bat
) else (
    echo No se encontró el entorno virtual. Cree uno con "python -m venv env".
    exit /b 1
)

REM Instala las dependencias
pip install -r requirements.txt

REM Ejecuta el script de automatización
python Facturar_Afip_V2.py

REM Desactiva el entorno virtual
deactivate
