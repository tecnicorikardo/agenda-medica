# 🔍 Checklist de Debug - WhatsApp Template Paciente

**Erro atual:** `(#132018) There's an issue with the parameters in your template`

---

## ✅ Passo 1: Confirmar Templates Aprovados ✓ COMPLETO

- ✅ **Médico:** `agenda_medico_resumo_v2` (FUNCIONANDO)
- ✅ **Paciente:** `agenda_paciente_lembrete` (ATIVO, Portuguese BR, 5 parâmetros, SEM botões)

---

## ✅ Passo 2: Verificar Variáveis no Render ✓ COMPLETO

Todas as variáveis estão corretas:
- ✅ `WHATSAPP_PATIENT_TEMPLATE_NAME` = `agenda_paciente_lembrete`
- ✅ `WHATSAPP_TEMPLATE_LANGUAGE` = `pt_BR`
- ✅ `WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE` = `standard`
- ✅ `WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT` = `0`

---

## ✅ Passo 3: Correções Aplicadas ✓ COMPLETO

- ✅ Removido `[TESTE]` do body (commit 98428af)
- ✅ Push realizado
- ✅ Aguardando redeploy

---

## 🔍 Passo 4: INVESTIGAR PARÂMETROS (ATUAL)

O erro #132018 significa que os **parâmetros** estão incorretos. Possíveis causas:

### Hipótese A: Formato da data/hora está errado
Template espera formato específico (ex: dd/mm/yyyy ou mm/dd/yyyy)

### Hipótese B: Parâmetros sendo enviados em ordem errada
Ordem esperada:
1. {{1}} = primeiro nome
2. {{2}} = data  
3. {{3}} = hora
4. {{4}} = clínica
5. {{5}} = médico

### Hipótese C: Algum parâmetro está vazio ou null

---

## 🎯 PRÓXIMA AÇÃO: Adicionar Log Detalhado

Vamos adicionar logs no código para ver EXATAMENTE o que está sendo enviado para a API do WhatsApp.

**Status:** ⬜ Em andamento

