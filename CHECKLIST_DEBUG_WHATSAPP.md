# 🔍 Checklist de Debug - WhatsApp Cloud API

## 📊 SITUAÇÃO ATUAL

**Status:** ✅ Sistema retorna "Enviado com sucesso" MAS ❌ Mensagens não chegam no WhatsApp

### Últimos Resultados do Teste:
- ✅ **Médico:** 5521970902074 — API retornou sucesso via template `agenda_medico_resumo_v2`
- ✅ **Paciente:** 5521986925971 — API retornou sucesso via template `agenda_paciente_lembrete`
- ❌ **Problema:** Nenhuma mensagem foi entregue nos dispositivos WhatsApp

---

## ✅ Correções Já Aplicadas

### Passo 1: Templates no Meta ✓
- ✅ **Médico:** `agenda_medico_resumo_v2` (Portuguese BR, 5 parâmetros, ATIVO)
- ✅ **Paciente:** `agenda_paciente_lembrete` (Portuguese BR, 5 parâmetros, SEM botões, ATIVO)
- ⚠️ **Status dos templates:** "Ativo — Qualidade pendente"

### Passo 2: Variáveis de Ambiente ✓
- ✅ `WHATSAPP_ACCESS_TOKEN` configurado
- ✅ `WHATSAPP_PHONE_NUMBER_ID` = `1142035782328806`
- ✅ `WHATSAPP_PATIENT_TEMPLATE_NAME` = `agenda_paciente_lembrete`
- ✅ `WHATSAPP_DOCTOR_TEMPLATE_NAME` = `agenda_medico_resumo_v2`
- ✅ `WHATSAPP_TEMPLATE_LANGUAGE` = `pt_BR`
- ✅ `WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE` = `standard`
- ✅ `WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT` = `0`

### Passo 3: Código ✓
- ✅ Removido prefixo `[TESTE]` que quebrava validação de templates
- ✅ Corrigido bug de código duplicado em `whatsapp.py`
- ✅ Adicionados logs de debug para rastreamento

---

## 🔍 Passo 4: DIAGNÓSTICO — API vs. Entrega (ATUAL)

O sistema mostra sucesso porque a **API do WhatsApp aceitou a requisição**, mas as mensagens **não estão sendo entregues** pelo Meta.

### Possíveis Causas:

#### A) Templates com "Qualidade pendente" ⚠️
- Templates novos têm entrega limitada até ganharem histórico positivo
- Meta pode estar bloqueando envios até o template ser aprovado completamente
- **Status atual:** "Ativo — Qualidade pendente" em ambos os templates

#### B) Números de teste não registrados 📱
- WhatsApp Business exige registro de números de teste no Meta Business Manager
- Caminho: Meta Business Manager → WhatsApp → Configurações → Números de telefone de teste

#### C) Cota de mensagens excedida 📊
- Tier inicial: 250 conversas/mês (1000 mensagens grátis)
- Após limite, mensagens são bloqueadas
- **Verificar em:** Meta Business Manager → WhatsApp → Insights

#### D) Problemas de validação do número do remetente 📞
- Phone Number ID pode estar incorreto ou não verificado
- **Verificar:** Se o número `1142035782328806` está ativo e verificado

---

## 🎯 PRÓXIMA AÇÃO: Verificar Logs Detalhados

### O que fazer AGORA:

1. **Rode o teste novamente:** https://agendadomedico.site/api/whatsapp/test

2. **Copie APENAS estas linhas dos logs do Render:**
   - Procure por: `WhatsApp patient template params:`
   - Procure por: `WhatsApp template payload:`
   - Estas linhas mostram os parâmetros exatos sendo enviados

3. **Cole aqui para análise**

---

## 📋 Verificações Pendentes no Meta Business Manager

- [ ] Ir em **Insights** → Verificar se mensagens aparecem como "Enviadas" mas não "Entregues"
- [ ] Ir em **Configurações** → Verificar status da qualidade dos templates
- [ ] Ir em **Configurações** → Adicionar números de teste (5521970902074 e 5521986925971)
- [ ] Verificar cota mensal de mensagens

**Status:** ⏳ Aguardando logs do próximo teste

