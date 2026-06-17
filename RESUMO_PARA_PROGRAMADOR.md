# Resumo Técnico - WhatsApp Integration

**TL;DR:** A Cloud API já está integrada. O envio confiável para médicos e pacientes depende de templates aprovados pela Meta e das variáveis corretas no Render.

---

## Problema Atual

**Sintoma:** mensagens por texto livre podem chegar para alguns médicos, mas pacientes ou outras contas podem não receber.  
**Causa:** a Meta só permite mensagem livre dentro da janela de conversa de 24h. Para lembrete automático/proativo, é obrigatório usar template aprovado.  
**Status:** templates ainda podem estar `PENDING`; use o verificador para confirmar.

---

## O que já funciona

```text
OK  WhatsApp Cloud API conectada
OK  Envio por texto livre aceito pela Meta quando existe janela de conversa
OK  Código de envio por template implementado
OK  E-mail continua funcionando
OK  App publicado no Render
```

---

## O que precisa estar configurado

No Render, tanto no **Web Service** quanto no **Cron Job**, configure manualmente:

```env
WHATSAPP_ACCESS_TOKEN=token_definitivo
WHATSAPP_PHONE_NUMBER_ID=id_do_numero
WHATSAPP_BUSINESS_ACCOUNT_ID=id_da_conta_whatsapp_business
WHATSAPP_API_VERSION=v20.0
WHATSAPP_TEMPLATE_LANGUAGE=pt_BR
WHATSAPP_PATIENT_TEMPLATE_NAME=nome_do_template_paciente
WHATSAPP_DOCTOR_TEMPLATE_NAME=nome_do_template_medico
```

Não grave tokens ou senhas no `render.yaml`.

---

## Mudanças Relevantes

- `backend/app/services/whatsapp.py`: integração com a Cloud API.
- `backend/app/services/whatsapp_templates.py`: renderização das mensagens e parâmetros dos templates.
- `backend/scripts/send_email_reminders.py`: envia e-mail + WhatsApp para pacientes e médicos.
- `backend/scripts/check_whatsapp_templates.py`: verifica número, WABA ID, idioma e status dos templates.
- `render.yaml`: define o cron job, mas deixa segredos como `sync: false` para preenchimento no painel do Render.

---

## Como Verificar Templates

```bash
python -m backend.scripts.check_whatsapp_templates
```

Resultado esperado:

```text
OK: Paciente '...' aprovado em pt_BR.
OK: Médico '...' aprovado em pt_BR.
```

Se aparecer `AGUARDANDO`, ainda é necessário esperar aprovação da Meta.

---

## Como Testar Envio Manual

No Shell do Render:

```bash
python -m backend.scripts.send_email_reminders --dias 1
```

Ou pela interface:

```text
Perfil -> Teste de WhatsApp -> Enviar WhatsApp de teste
```

O teste do paciente só funciona se houver consulta futura para o médico logado e telefone válido no cadastro do paciente.

---

## Fluxo Automático

```text
1. Cron do Render roda às 11:00 UTC (08:00 America/Sao_Paulo)
2. Script busca consultas em D+1 e D+2
3. Envia e-mail para paciente e resumo por e-mail para médico
4. Envia WhatsApp por template, se configurado e aprovado
5. Registra status na tabela lembretes
```

---

## Pontos de Atenção

- `WHATSAPP_PHONE_NUMBER_ID` é o ID do número, não o telefone com DDD.
- `WHATSAPP_BUSINESS_ACCOUNT_ID` é o WABA ID usado para listar templates.
- Templates precisam existir no idioma configurado em `WHATSAPP_TEMPLATE_LANGUAGE`.
- Se o token apareceu em conversa, gere outro token definitivo e atualize no Render.
- Texto livre pode retornar sucesso na API e ainda assim não entregar fora da janela de 24h; para lembretes, use template.
