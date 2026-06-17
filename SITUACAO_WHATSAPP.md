# Situação Atual - WhatsApp Business API

**Data:** 17/06/2026  
**Projeto:** Agenda Médica

---

## Objetivo

Enviar lembretes automáticos de consultas por WhatsApp para pacientes e médicos, mantendo o envio por e-mail existente.

---

## Diagnóstico

O WhatsApp Cloud API está integrado e a Meta aceita chamadas autenticadas. O comportamento observado tem uma explicação importante:

- Mensagem de **texto livre** só funciona quando a conversa foi iniciada recentemente pelo destinatário, dentro da janela de 24h.
- Para lembretes automáticos, especialmente primeira mensagem para paciente, a Meta exige **template aprovado**.
- Enquanto o template estiver `PENDING`, a API pode retornar erro de template ou aceitar texto livre sem entregar para todos os números.

---

## O que já está funcionando

- Serviço de envio via WhatsApp Cloud API.
- Normalização de telefones para formato internacional.
- Rota de teste em `POST /api/whatsapp/test`.
- UI em `Perfil -> Teste de WhatsApp`.
- Registro de lembretes na tabela `lembretes`.
- Envio por e-mail preservado.
- Cron job definido em `render.yaml`.

---

## Configuração Necessária no Render

Configure manualmente no painel do Render, no **Web Service** e no **Cron Job**:

```env
WHATSAPP_ACCESS_TOKEN=token_definitivo
WHATSAPP_PHONE_NUMBER_ID=id_do_numero
WHATSAPP_BUSINESS_ACCOUNT_ID=id_da_conta_whatsapp_business
WHATSAPP_API_VERSION=v20.0
WHATSAPP_TEMPLATE_LANGUAGE=pt_BR
WHATSAPP_PATIENT_TEMPLATE_NAME=nome_do_template_paciente
WHATSAPP_DOCTOR_TEMPLATE_NAME=nome_do_template_medico
```

Também configure no Cron Job as mesmas credenciais de e-mail usadas no Web Service.

> Segurança: não grave `WHATSAPP_ACCESS_TOKEN`, senha SMTP ou outras credenciais no Git.

---

## Como Verificar os Templates

Execute em um ambiente com as variáveis do WhatsApp configuradas:

```bash
python -m backend.scripts.check_whatsapp_templates
```

O verificador confirma:

- se o token acessa o `WHATSAPP_PHONE_NUMBER_ID`;
- se `WHATSAPP_BUSINESS_ACCOUNT_ID` lista templates corretamente;
- se os templates configurados existem no idioma `pt_BR`;
- se estão `APPROVED`, `PENDING` ou `REJECTED`.

Status esperado para envio automático:

```text
OK: Paciente '...' aprovado em pt_BR.
OK: Médico '...' aprovado em pt_BR.
```

---

## Como Testar

### Pela interface

1. Acesse o Render: `https://agenda-medica-2c9b.onrender.com`
2. Faça login.
3. Vá em `Perfil`.
4. Clique em `Enviar WhatsApp de teste`.

O teste do paciente exige:

- paciente cadastrado com telefone válido;
- consulta futura para o médico logado;
- template aprovado, ou conversa aberta nas últimas 24h se estiver usando texto livre.

### Pelo Shell do Render

```bash
python -m backend.scripts.send_email_reminders --dias 1
```

---

## Cron Job

O cron está definido no `render.yaml`:

```yaml
dockerCommand: python -m backend.scripts.send_email_reminders --dias 1 --dias 2
schedule: "0 11 * * *"
```

`11:00 UTC` equivale a `08:00` em `America/Sao_Paulo`.

Após alterar o `render.yaml`, faça commit/push e confira no painel do Render se o cron foi criado/atualizado. Depois preencha as variáveis marcadas como `sync: false`.

---

## Problemas Comuns

### Template name does not exist in the translation

Prováveis causas:

- template ainda está `PENDING`;
- nome do template no Render não bate com o nome na Meta;
- idioma no Render não bate com o idioma do template;
- `WHATSAPP_BUSINESS_ACCOUNT_ID` aponta para outra conta WhatsApp Business.

### Texto livre retorna sucesso, mas não chega

Isso acontece fora da janela de conversa de 24h. Para lembretes automáticos, use templates aprovados.

### Médico recebe, paciente não

O médico pode ter conversa aberta com o número comercial. O paciente precisa de template aprovado ou conversa aberta.

### Outra conta médica não recebe

Confira:

- telefone do médico no perfil;
- consulta futura para testar paciente;
- telefone do paciente;
- templates aprovados e configurados;
- variáveis do Render no Web Service e no Cron Job.

---

## Checklist

- [ ] Token definitivo gerado após qualquer exposição acidental.
- [ ] `WHATSAPP_PHONE_NUMBER_ID` configurado no Render.
- [ ] `WHATSAPP_BUSINESS_ACCOUNT_ID` configurado no Render.
- [ ] Templates existem em `pt_BR`.
- [ ] Templates estão `APPROVED`.
- [ ] Web Service redeployado após alterar variáveis.
- [ ] Cron Job com as mesmas variáveis do Web Service.
- [ ] Teste manual do médico.
- [ ] Teste manual do paciente com consulta futura.
- [ ] Logs do cron monitorados no Render.
