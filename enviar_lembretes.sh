#!/bin/bash

echo "================================================"
echo "  Envio de Lembretes - Agenda Medica"
echo "================================================"
echo ""
echo "Ativando ambiente virtual..."
source venv/Scripts/activate
echo ""
echo "Enviando lembretes para consultas de amanha..."
python -m backend.scripts.send_email_reminders --dias 1
echo ""
echo "================================================"
echo "  Concluido!"
echo "================================================"
