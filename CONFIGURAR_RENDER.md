# 🚀 Configurações do WhatsApp para o Render

**Data:** 17/06/2026  
**Urgente:** Configurar estas variáveis para corrigir erro #132018

---

## ⚠️ Problema Atual

**Erro do paciente:** `(#132018) There's an issue with the parameters in your template`

**Causa:** Faltam duas variáveis de configuração no Render

---

## ✅ Solução

Adicione estas **2 variáveis** no painel do Render:

### 1. Acessar Render
- URL: https://render.com
- Login: rikardomartinssantos@gmail.com
- Projeto: **agenda-medica**

### 2. Adicionar variáveis no Web Service

Vá em: **Environment** → **Environment Variables** → **Add Environment Variable**

Adicione:

```env
WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE=standard
WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT=0
```

### 3. Adicionar variáveis no Cron Job (se existir)

Vá em: **agenda-medica-lembretes** → **Environment** → **Environment Variables**

Adicione as mesmas variáveis:

```env
WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE=standard
WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT=0
```

---

## 📋 Variáveis Completas do WhatsApp

Para referência, todas as variáveis do WhatsApp que devem estar configuradas:

```env
# Obrigatórias (já configuradas)
WHATSAPP_ACCESS_TOKEN=EAASvTuvlqRE... (seu token)
WHATSAPP_PHONE_NUMBER_ID=1092534873945633

# Opcionais mas recomendadas (já configuradas)
WHATSAPP_API_VERSION=v20.0
WHATSAPP_DEFAULT_COUNTRY_CODE=55
WHATSAPP_TEMPLATE_LANGUAGE=pt_BR

# Templates aprovados (já configuradas)
WHATSAPP_PATIENT_TEMPLATE_NAME=agenda_paciente_h
WHATSAPP_DOCTOR_TEMPLATE_NAME=agenda_medico_re

# NOVAS - precisam ser adicionadas AGORA ✅
WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE=standard
WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT=0
```

---

## 🔍 O que cada variável faz

### WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE
**Valor:** `standard`  
**Função:** Define que os parâmetros serão enviados no formato padrão (5 parâmetros posicionais)  
**Alternativa:** `message` (envia apenas a mensagem renderizada completa)

### WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT
**Valor:** `0`  
**Função:** Define que o template NÃO tem botões  
**Alternativa:** `2` (se o template tiver botões "Confirmar" e "Cancelar")

---

## ✅ Após configurar

1. **Salvar as variáveis** no Render
2. O Render vai **fazer redeploy automaticamente**
3. **Testar novamente** no perfil do sistema
4. Médico e paciente devem receber as mensagens ✅

---

## 🧪 Como testar

1. Acessar: https://agenda-medica-2c9b.onrender.com (ou sua URL)
2. Login no sistema
3. Ir em: **Perfil** → **Notificações**
4. Clicar em: **Testar WhatsApp**
5. Verificar que ambos (médico e paciente) receberam ✅

---

## 📞 Referências

- **Documentação completa:** `docs/WHATSAPP_TEMPLATES.md`
- **Relatório de implementações:** `RELATORIO_IMPLEMENTACOES_2026-06-19.md`
- **Situação atual:** `SITUACAO_WHATSAPP.md`

---

**Criado em:** 17/06/2026  
**Atualizado em:** 17/06/2026
