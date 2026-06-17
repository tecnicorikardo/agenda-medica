# Guia de Templates do WhatsApp Business

## 📋 Problema Atual

O WhatsApp Business API da Meta **requer templates aprovados** para enviar mensagens para clientes (pacientes). Mensagens de texto simples só funcionam em conversas já iniciadas (nos últimos 24h).

## 🔧 Variáveis no .env

Agora corrigidas:
```bash
WHATSAPP_ACCESS_TOKEN="seu_token_aqui"
WHATSAPP_PHONE_NUMBER_ID="seu_phone_id_aqui"
WHATSAPP_BUSINESS_ACCOUNT_ID="sua_conta_whatsapp_business_id"
WHATSAPP_PATIENT_TEMPLATE_NAME=""  # Nome do template aprovado para pacientes
WHATSAPP_DOCTOR_TEMPLATE_NAME=""   # Nome do template aprovado para médicos
```

## 📝 Como Criar Templates no Meta Business Manager

### 1. Acesse o Meta Business Manager
- Vá para: https://business.facebook.com/
- Acesse **WhatsApp Manager** → **Message Templates**

### 2. Criar Template para Pacientes

**Nome sugerido:** `lembrete_consulta_paciente`

**Categoria:** Utility (para lembretes)

**Idioma:** Portuguese (BR)

**Conteúdo do template:**
```
Olá, {{1}}!

Lembramos que você tem uma consulta marcada para {{2}} às {{3}}.

Clínica: {{4}}
Médico(a): {{5}}

Confirme sua presença ou entre em contato com antecedência caso precise remarcar.
```

**Variáveis (em ordem):**
1. `{{1}}` - Primeiro nome do paciente
2. `{{2}}` - Data (dd/mm/yyyy)
3. `{{3}}` - Hora (HH:MM)
4. `{{4}}` - Nome da clínica
5. `{{5}}` - Nome do médico

### 3. Criar Template para Médicos

**Nome sugerido:** `resumo_agenda_medico`

**Categoria:** Utility

**Idioma:** Portuguese (BR)

**Conteúdo do template:**
```
Olá, {{1}}!

Sua agenda de {{2}} tem {{3}} consulta(s).

{{4}}

Clínica: {{5}}
```

**Variáveis (em ordem):**
1. `{{1}}` - Nome do médico
2. `{{2}}` - Data (dd/mm/yyyy)
3. `{{3}}` - Número de consultas
4. `{{4}}` - Resumo das consultas (lista)
5. `{{5}}` - Nome da clínica

### 4. Submeter para Aprovação

- Clique em **Submit** para cada template
- A Meta pode levar de **algumas horas até 48h** para aprovar
- Você receberá notificação por e-mail quando aprovado

### 5. Status dos Templates

Para verificar o status, execute:

```powershell
$wabaId = "SEU_WABA_ID"
$token = "SEU_ACCESS_TOKEN"

Invoke-RestMethod `
  -Uri "https://graph.facebook.com/v20.0/$wabaId/message_templates?fields=name,status,category,language&access_token=$token"
```

**Status possíveis:**
- `PENDING` - Aguardando aprovação
- `APPROVED` - Aprovado e pronto para usar
- `REJECTED` - Rejeitado (verifique o motivo)

### 6. Atualizar o .env

Após aprovação, atualize:
```bash
WHATSAPP_PATIENT_TEMPLATE_NAME="lembrete_consulta_paciente"
WHATSAPP_DOCTOR_TEMPLATE_NAME="resumo_agenda_medico"
WHATSAPP_BUSINESS_ACCOUNT_ID="SEU_WABA_ID"
```

## 🔍 Como o Código Funciona

O código em `backend/app/services/whatsapp.py` verifica:

```python
async def send_whatsapp_message(
    *,
    to: str,
    body: str,
    template_name: str = "",
    language_code: str = "pt_BR",
    template_parameters: list[str] | None = None,
) -> WhatsAppResult:
    if template_name:
        # Usa template aprovado (NECESSÁRIO para primeira mensagem)
        return await send_whatsapp_template(...)
    
    # Usa texto simples (só funciona em conversas ativas)
    return await send_whatsapp_text(...)
```

## ⚠️ Importante

1. **Primeira mensagem = SEMPRE template aprovado**
2. **Mensagens dentro de 24h da resposta do cliente = texto simples OK**
3. **Templates podem ter até 1024 caracteres**
4. **Variáveis são obrigatórias se definidas no template**
5. **A ordem das variáveis importa!**

## 🧪 Testar Após Aprovação

1. Atualize o `.env` com os nomes dos templates aprovados
2. Reinicie o servidor backend
3. Execute o teste:

```bash
python -m backend.scripts.send_email_reminders --dias 1
```

## 📞 Troubleshooting

### Erro: "Template not found"
- Verifique se o nome está correto no `.env`
- Confirme que o template está `APPROVED`
- Confirme que `WHATSAPP_BUSINESS_ACCOUNT_ID` é a conta WhatsApp Business onde o template foi criado

### Erro: "Parameter count mismatch"
- Verifique se está passando o número correto de variáveis
- A ordem deve corresponder aos `{{1}}`, `{{2}}`, etc.

### Erro: "Recipient phone not valid"
- O telefone deve estar no formato internacional sem `+`
- Exemplo: `5511999999999` (código país + DDD + número)

### Paciente não recebe
- Template deve estar **APPROVED**
- Telefone do paciente deve estar correto
- Conta do WhatsApp Business deve estar ativa

## 🔗 Links Úteis

- [Meta Business Manager](https://business.facebook.com/)
- [Documentação Templates](https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/cloud-api)
