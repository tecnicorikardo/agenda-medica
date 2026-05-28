# Agenda Médica — Documentação do Projeto

> Última atualização: Maio/2026

---

## 📋 Visão Geral

Sistema web de gestão de consultório médico. Permite gerenciar consultas, pacientes, lembretes automáticos por e-mail e notificações push.

- **URL de produção:** https://agenda-medica-2c9b.onrender.com
- **Repositório:** https://github.com/tecnicorikardo/agenda-medica

---

## 🏗️ Stack Tecnológica

### Backend
| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12 | Linguagem |
| FastAPI | 0.115 | Framework web |
| SQLAlchemy | 2.0 | ORM |
| Alembic | 1.14 | Migrations do banco |
| Pydantic v2 | 2.11 | Validação de dados |
| python-jose | 3.5 | JWT (autenticação) |
| passlib + bcrypt | - | Hash de senhas |
| APScheduler | 3.10 | Scheduler (lembretes às 08h) |
| aiohttp | 3.11 | Chamadas HTTP (Brevo/Resend) |
| aiosmtplib | 3.0 | SMTP local |
| openpyxl | 3.1 | Export/Import Excel |
| reportlab | 4.2 | Geração de PDF |
| pywebpush | 2.0 | Web Push (VAPID) |

### Frontend
| Tecnologia | Função |
|---|---|
| HTML/CSS/JS puro | SPA sem framework |
| Service Worker | PWA / cache offline |
| Web Push API | Notificações push |
| WebAuthn | Login biométrico (Face ID) |

### Banco de Dados
| Tabela | Função |
|---|---|
| `usuarios` | Médicos cadastrados |
| `pacientes` | Pacientes do consultório |
| `consultas` | Agendamentos |
| `lembretes` | Registro de lembretes enviados |
| `push_subscriptions` | Dispositivos para notificação push |

---

## ☁️ Serviços e Contas

### Render (hospedagem)
- **URL:** https://dashboard.render.com
- **Conta:** helogourmet2@gmail.com
- **Plano:** Free
- **Serviços ativos:**
  - `agenda-medica` — Web Service (Docker)
  - `agenda-medica-db` — PostgreSQL (Free)

### GitHub (repositório)
- **URL:** https://github.com/tecnicorikardo/agenda-medica
- **Conta:** tecnicorikardo
- **Branch principal:** main
- **Deploy automático:** sim (push → Render redeploy)

### Brevo (envio de e-mail transacional)
- **URL:** https://app.brevo.com
- **Conta:** helogourmet2@gmail.com
- **Plano:** Free (300 e-mails/dia)
- **Método usado:** API HTTP (não SMTP — porta bloqueada no Render)
- **Variável de ambiente:** `BREVO_API_KEY`

### Resend (e-mail — configurado mas não usado ativamente)
- **URL:** https://resend.com
- **Conta:** helogourmet2@gmail.com
- **Plano:** Free (3.000 e-mails/mês)
- **Limitação:** sem domínio verificado, só envia para o e-mail da própria conta
- **Variável de ambiente:** `RESEND_API_KEY`

---

## 🔧 Variáveis de Ambiente (Render)

> ⚠️ Nunca commitar valores reais. Gerenciar em: Render → agenda-medica → Environment

| Variável | Descrição | Exemplo |
|---|---|---|
| `DATABASE_URL` | URL do PostgreSQL (Render) | `postgresql://user:pass@host/db` |
| `JWT_SECRET_KEY` | Chave secreta JWT (gerada pelo Render) | `abc123...` |
| `AUTH_COOKIE_SECURE` | Cookie seguro em produção | `true` |
| `APP_TIMEZONE` | Fuso horário do scheduler | `America/Sao_Paulo` |
| `APP_NAME` | Nome do app | `Agenda Médica` |
| `BREVO_API_KEY` | Chave API do Brevo | `xkeysib-...` |
| `RESEND_API_KEY` | Chave API do Resend | `re_...` |
| `SMTP_FROM_EMAIL` | E-mail remetente | `helogourmet2@gmail.com` |
| `SMTP_FROM_NAME` | Nome remetente | `Agenda Médica` |
| `RESET_SECRET` | Senha para reset manual de conta | `(definido no Render)` |
| `VAPID_PUBLIC_KEY` | Chave pública Web Push | `(opcional)` |
| `VAPID_PRIVATE_KEY` | Chave privada Web Push | `(opcional)` |
| `VAPID_MAILTO` | E-mail para VAPID | `mailto:...` |

---

## 📁 Estrutura do Projeto

```
agenda-medica/
├── alembic/                    # Migrations do banco
│   ├── env.py
│   └── versions/
│       └── 0001_initial_schema.py
├── alembic.ini                 # Config do Alembic
├── backend/
│   └── app/
│       ├── api/
│       │   ├── router.py       # Registra todas as rotas
│       │   └── routes/
│       │       ├── auth.py         # Login, cadastro, perfil, senha
│       │       ├── appointments.py # CRUD de consultas
│       │       ├── patients.py     # CRUD de pacientes + Excel + PDF
│       │       ├── dashboard.py    # KPIs do dia
│       │       ├── push.py         # Web Push (VAPID)
│       │       └── email_test.py   # Endpoint de teste de e-mail
│       ├── core/
│       │   ├── config.py       # Variáveis de ambiente (pydantic-settings)
│       │   └── security.py     # JWT, bcrypt
│       ├── crud/               # Queries ao banco
│       ├── db/
│       │   ├── base.py         # DeclarativeBase
│       │   └── session.py      # Engine + SessionLocal
│       ├── models/             # ORM (SQLAlchemy mapped_column)
│       ├── schemas/            # Pydantic schemas
│       ├── services/
│       │   ├── email.py        # Brevo API → Resend → SMTP
│       │   ├── email_templates.py  # Templates HTML dos e-mails
│       │   ├── push.py         # Web Push via pywebpush
│       │   └── scheduler.py    # APScheduler — roda às 08h
│       ├── utils/
│       │   ├── deps.py         # get_current_user (JWT cookie)
│       │   └── pdf.py          # Geração de PDF com reportlab
│       └── main.py             # FastAPI app + lifespan
├── backend/scripts/
│   ├── migrate.py              # Roda alembic upgrade head
│   ├── create_user.py          # Cria primeiro usuário via CLI
│   └── send_email_reminders.py # Script manual de lembretes
├── frontend/
│   ├── index.html
│   ├── app.js                  # SPA completa (~3000 linhas)
│   ├── app.css                 # Estilos (~1800 linhas)
│   ├── sw.js                   # Service Worker (PWA)
│   ├── manifest.json           # PWA manifest
│   └── icons/                  # Ícones PWA (72px a 512px)
├── docs/
│   ├── PROJETO.md              # Este arquivo
│   ├── FUNCIONALIDADES.md      # Guia completo de funcionalidades
│   └── supabase_schema.sql     # Schema SQL original (referência)
├── Dockerfile                  # Build Docker (usado pelo Render)
├── Procfile                    # Comando de start (Railway/Heroku)
├── render.yaml                 # Blueprint do Render (infra como código)
├── requirements.txt            # Dependências Python
└── .env.example                # Exemplo de variáveis de ambiente
```

---

## 🚀 Como Fazer Deploy

### Render (atual)
1. Push para `main` no GitHub
2. Render detecta automaticamente e redeploy
3. Migrations rodam automaticamente no startup (`python -m backend.scripts.migrate`)

### Local
```bash
# 1. Instalar dependências
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar .env (copiar .env.example)
cp .env.example .env
# editar DATABASE_URL e JWT_SECRET_KEY

# 3. Rodar migrations
python -m backend.scripts.migrate

# 4. Criar primeiro usuário
python -m backend.scripts.create_user

# 5. Iniciar servidor
uvicorn backend.app.main:app --reload
```

---

## 📧 Fluxo de E-mails

```
Scheduler (08:00 diário)
    └── send_email_reminders.py
        ├── Para cada médico com lembrete ativo:
        │   ├── Busca consultas de amanhã (e/ou 2 dias)
        │   ├── Envia e-mail para cada PACIENTE com e-mail cadastrado
        │   └── Envia resumo do dia para o MÉDICO
        └── Registra na tabela `lembretes` (evita duplicatas)

Provedor de e-mail (prioridade):
    1. Brevo API (BREVO_API_KEY)     ← atual
    2. Resend API (RESEND_API_KEY)
    3. SMTP direto (local apenas)
```

---

## 🔐 Autenticação

- Login via e-mail + senha
- Sessão mantida em **cookie HttpOnly** (7 dias)
- JWT assinado com `JWT_SECRET_KEY`
- Suporte a **biometria** (WebAuthn / Face ID) após primeiro login
- Recuperação de senha via e-mail (senha temporária)

---

## 📱 PWA

- Instalável na tela inicial (Android e iOS)
- Cache offline via Service Worker
- Notificações push via Web Push (VAPID) — requer configurar `VAPID_*`
- Para gerar chaves VAPID: `python -m backend.scripts.gen_vapid`

---

## 🗺️ Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| POST | `/api/auth/cadastro` | Criar conta |
| GET | `/api/auth/me` | Usuário logado |
| POST | `/api/auth/esqueci-senha` | Enviar senha temporária |
| POST | `/api/auth/alterar-senha` | Alterar senha |
| PUT | `/api/auth/perfil` | Atualizar perfil |
| POST | `/api/auth/perfil/avatar` | Upload de foto |
| DELETE | `/api/auth/perfil/avatar` | Remover foto |
| POST | `/api/auth/reset-direto` | Reset manual (requer RESET_SECRET) |
| GET | `/api/dashboard` | KPIs do dia |
| GET | `/api/appointments` | Consultas do dia |
| GET | `/api/appointments/range` | Consultas por período |
| POST | `/api/appointments` | Criar consulta |
| PUT | `/api/appointments/{id}` | Editar consulta |
| POST | `/api/appointments/{id}/cancel` | Cancelar |
| POST | `/api/appointments/{id}/status/{s}` | Mudar status |
| GET | `/api/patients` | Listar pacientes |
| POST | `/api/patients` | Criar paciente |
| PUT | `/api/patients/{id}` | Editar paciente |
| DELETE | `/api/patients/{id}` | Excluir paciente |
| GET | `/api/patients/{id}/history` | Histórico |
| GET | `/api/patients/{id}/history/pdf` | PDF do histórico |
| GET | `/api/patients/export/excel` | Exportar Excel |
| POST | `/api/patients/import/excel` | Importar Excel |
| GET | `/api/push/vapid-public-key` | Chave VAPID pública |
| POST | `/api/push/subscribe` | Registrar dispositivo |
| POST | `/api/push/test` | Testar push |
| POST | `/api/email/test` | Testar e-mail |
| GET | `/api/health` | Health check |
