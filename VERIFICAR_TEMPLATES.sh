#!/bin/bash

echo "======================================"
echo "  Verificador de Templates WhatsApp"
echo "======================================"
echo ""
echo "Ativando ambiente virtual..."
source venv/Scripts/activate
echo ""
python -m backend.scripts.check_whatsapp_templates
echo ""
