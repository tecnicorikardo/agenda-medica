@echo off
echo ================================================
echo   Envio de Lembretes - Agenda Medica
echo ================================================
echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo Enviando lembretes para consultas de amanha...
python -m backend.scripts.send_email_reminders --dias 1
echo.
echo ================================================
echo   Concluido!
echo ================================================
pause
