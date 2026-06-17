# 🚀 Como Usar - Agenda Médica

## 📦 Instalação Inicial (Apenas uma vez)

### 1. Criar o ambiente virtual:
```bash
python -m venv venv
```

### 2. Ativar o ambiente virtual:

**No Windows (CMD ou PowerShell):**
```bash
venv\Scripts\activate
```

**No Git Bash:**
```bash
source venv/Scripts/activate
```

### 3. Instalar as dependências:
```bash
pip install -r requirements.txt
```

---

## 🏃 Executando o Sistema

### Opção 1: Usando Scripts Prontos (Recomendado)

#### Windows:
- **Enviar lembretes:** Clique duplo em `enviar_lembretes.bat`
- **Verificar templates WhatsApp:** Clique duplo em `VERIFICAR_TEMPLATES.bat`

#### Git Bash / Linux:
```bash
# Enviar lembretes
bash enviar_lembretes.sh

# Verificar templates WhatsApp
bash VERIFICAR_TEMPLATES.sh
```

### Opção 2: Comandos Manuais

**Sempre ative o ambiente virtual primeiro:**

```bash
# Windows CMD
venv\Scripts\activate

# Git Bash / Linux
source venv/Scripts/activate
```

**Depois execute os comandos:**

```bash
# Enviar lembretes para amanhã (1 dia antes)
python -m backend.scripts.send_email_reminders --dias 1

# Enviar lembretes para daqui 2 dias
python -m backend.scripts.send_email_reminders --dias 2

# Enviar lembretes para 1 e 2 dias antes
python -m backend.scripts.send_email_reminders --dias 1 --dias 2

# Verificar status dos templates do WhatsApp
python -m backend.scripts.check_whatsapp_templates
```

---

## ⚙️ Configuração do WhatsApp

### 1. Verificar se está configurado:
```bash
bash VERIFICAR_TEMPLATES.sh
```

### 2. O que você verá:

**Se os templates estiverem aprovados:**
```
OK: Paciente 'nome_do_template_paciente' aprovado em pt_BR.
OK: Médico 'nome_do_template_medico' aprovado em pt_BR.
```

**Se ainda estiverem em análise:**
```
AGUARDANDO: Paciente 'nome_do_template_paciente' em pt_BR está com status: PENDING.
AGUARDANDO: Médico 'nome_do_template_medico' em pt_BR está com status: PENDING.
```

### 3. Após aprovação:

Configure os templates aprovados no `.env` ou no Render:
```env
WHATSAPP_BUSINESS_ACCOUNT_ID="id_da_conta_whatsapp_business"
WHATSAPP_PATIENT_TEMPLATE_NAME="nome_do_template_paciente"
WHATSAPP_DOCTOR_TEMPLATE_NAME="nome_do_template_medico"
```

Apenas **reinicie o servidor backend** e os lembretes via WhatsApp começarão a funcionar!

---

## 🔧 Agendamento Automático (Opcional)

### Windows - Agendador de Tarefas

1. Abra o **Agendador de Tarefas** do Windows
2. Crie uma nova tarefa básica
3. Configure para executar diariamente às 08:00
4. Ação: Executar o arquivo `enviar_lembretes.bat`

### Linux/Mac - Crontab

Edite o crontab:
```bash
crontab -e
```

Adicione a linha (executa todo dia às 08:00):
```cron
0 8 * * * cd /caminho/para/agendamedica && bash enviar_lembretes.sh
```

---

## 🐛 Solução de Problemas

### Erro: "No module named 'sqlalchemy'"
**Causa:** Ambiente virtual não está ativado ou dependências não instaladas.

**Solução:**
```bash
# Ativar ambiente virtual
source venv/Scripts/activate  # Git Bash
# ou
venv\Scripts\activate  # Windows CMD

# Instalar dependências
pip install -r requirements.txt
```

### Erro: "DATABASE_URL não definido"
**Causa:** Arquivo `.env` não encontrado ou variável não configurada.

**Solução:** Verifique se o arquivo `.env` existe na raiz do projeto com:
```env
DATABASE_URL="postgresql://..."
```

### Erro: "WHATSAPP_ACCESS_TOKEN não definido"
**Causa:** Variáveis do WhatsApp não configuradas no `.env`.

**Solução:** Configure no `.env`:
```env
WHATSAPP_ACCESS_TOKEN="seu_token"
WHATSAPP_PHONE_NUMBER_ID="seu_phone_id"
WHATSAPP_BUSINESS_ACCOUNT_ID="seu_waba_id"
```

### Templates não funcionam
**Causa:** Templates ainda não foram aprovados pelo Meta.

**Solução:**
1. Execute: `bash VERIFICAR_TEMPLATES.sh`
2. Aguarde aprovação do Meta (até 48h)
3. Após aprovação, reinicie o servidor

---

## 📞 Suporte

- **Documentação WhatsApp:** `docs/WHATSAPP_TEMPLATES.md`
- **Funcionalidades:** `docs/FUNCIONALIDADES.md`
- **Configurações:** Arquivo `.env` na raiz do projeto

---

**Agenda Médica** - Sistema de gestão de consultório médico
