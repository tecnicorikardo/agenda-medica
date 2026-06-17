@echo off
echo ======================================
echo   Verificador de Templates WhatsApp
echo ======================================
echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
python -m backend.scripts.check_whatsapp_templates
echo.
pause
