# Confirmação de consultas pelo WhatsApp

## Fluxo

1. O cron `agenda-medica-whatsapp-confirmacoes` roda a cada 10 minutos.
2. Cada médico usa seus horários configurados, por padrão 24 e 2 horas antes.
3. O paciente recebe o template aprovado com dois botões:
   - índice `0`: `Confirmar Consulta`
   - índice `1`: `Cancelar Consulta`
4. A Meta envia a resposta para `POST /api/webhooks/whatsapp`.
5. O sistema valida a assinatura, identifica o lembrete e o telefone do paciente,
   atualiza a consulta e envia a mensagem personalizada de retorno.

## Configuração da Meta

No aplicativo do Meta for Developers, configure:

- Callback URL: `https://SEU_DOMINIO/api/webhooks/whatsapp`
- Verify token: o mesmo valor de `WHATSAPP_VERIFY_TOKEN`
- Campo do webhook: `messages`

O template de paciente deve estar aprovado e possuir dois botões de resposta
rápida na ordem descrita acima.

## Variáveis de ambiente

```env
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_PATIENT_TEMPLATE_NAME=
WHATSAPP_TEMPLATE_LANGUAGE=pt_BR
WHATSAPP_VERIFY_TOKEN=
WHATSAPP_APP_SECRET=
WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE=standard
```

`WHATSAPP_APP_SECRET` é o segredo do aplicativo Meta e protege o endpoint com a
assinatura `X-Hub-Signature-256`.

### Modos de parâmetros

- `standard`: usa os cinco parâmetros já documentados no template atual:
  primeiro nome, data, hora, clínica e médico.
- `message`: usa um único parâmetro contendo a mensagem inteira personalizada.
  Só habilite se o template aprovado na Meta tiver exatamente esse formato.

As mensagens de confirmação e cancelamento são personalizáveis integralmente,
pois o clique do paciente abre a janela de atendimento do WhatsApp.

## Variáveis dos templates internos

- `{paciente}`
- `{medico}`
- `{data}`
- `{hora}`
- `{data_hora}`
- `{clinica}`
- `{telefone}`

Os templates são sempre consultados por `medico_id`.

## Persistência

- `templates_whatsapp`: mensagens individuais de cada médico.
- `interacoes_whatsapp`: eventos recebidos, enviados e status da Meta.
- `consultas.data_confirmacao`: data da confirmação.
- `consultas.data_cancelamento`: data do cancelamento.
- `lembretes.chave_idempotencia`: impede lembretes duplicados para a mesma
  consulta e antecedência.

## Teste

No perfil do médico:

1. Configure os horários e as três mensagens.
2. Cadastre uma consulta futura com telefone válido.
3. Use `Enviar WhatsApp de teste`.
4. Clique em cada botão e confirme a atualização do status na agenda.
