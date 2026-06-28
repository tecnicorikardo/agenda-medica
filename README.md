# Agenda Médica (web)

Sistema web profissional para agenda médica, pensado para uso real no dia a dia (rua + consultório) e funcionando bem no celular e no desktop.

## Tecnologias

- **Frontend:** HTML/CSS/JS responsivo (SPA leve)
- **Backend:** Python + FastAPI
- **Banco:** PostgreSQL (qualquer provedor — Render, Railway, local, etc.)
- **Migrations:** Alembic (tabelas criadas automaticamente no primeiro deploy)
- **Deploy:** Render (render.yaml pronto) ou qualquer serviço com suporte a Docker

## Estrutura do projeto

```
backend/    API, autenticação, regras de agenda, modelos e endpoints
frontend/   interface web responsiva
alembic/    migrations do banco de dados
docs/       documentação
```

## Documentação para desenvolvedores

- [`docs/GUIA_DESENVOLVEDOR.md`](docs/GUIA_DESENVOLVEDOR.md) — ponto de partida para entender arquitetura, contas, variáveis de ambiente, rotas, banco, deploy, scripts e testes.
- [`docs/FUNCIONALIDADES.md`](docs/FUNCIONALIDADES.md) — visão funcional do produto.
- [`docs/WHATSAPP_TEMPLATES.md`](docs/WHATSAPP_TEMPLATES.md) e [`docs/WHATSAPP_CONFIRMACAO.md`](docs/WHATSAPP_CONFIRMACAO.md) — integração WhatsApp Cloud API.
- [`COMO_USAR.md`](COMO_USAR.md) — comandos operacionais rápidos.

Credenciais reais não devem ser versionadas. Use `.env` para desenvolvimento local e o painel do Render/Meta/GitHub/Mercado Pago para produção. Se precisar registrar contas internas do projeto, use `MINHAS_CONTAS.md`, que é ignorado pelo Git.

## Como rodar localmente

### 1) Criar banco PostgreSQL local

Você pode usar Docker para subir um Postgres rapidamente:

```bash
docker run -d --name agenda-db -e POSTGRES_PASSWORD=senha -e POSTGRES_DB=agenda_medica -p 5432:5432 postgres:16
```

Ou use qualquer instalação local de PostgreSQL.

### 2) Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e ajuste pelo menos:
- `DATABASE_URL` — string de conexão com o banco
- `JWT_SECRET_KEY` — chave secreta (gere com `python -c "import secrets; print(secrets.token_hex(32))"`)

### 3) Instalar dependências

```bash
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 4) Rodar migrations (cria as tabelas)

```bash
python -m backend.scripts.migrate
```

### 5) Criar o primeiro usuário

```bash
python -m backend.scripts.create_user
```

### 6) Iniciar o servidor

```bash
uvicorn backend.app.main:app --reload
```

Abra: `http://localhost:8000`

---

## Deploy no Render (recomendado)

### Opção A — render.yaml (automático)

1. Suba o repositório no GitHub
2. No Render, clique em **New → Blueprint** e selecione o repositório
3. O Render vai ler o `render.yaml` e criar automaticamente:
   - Um **Web Service** (Docker) para o app
   - Um **PostgreSQL** gratuito vinculado ao app
4. Aguarde o build. As migrations rodam automaticamente no startup.
5. Após o deploy, abra o Shell do serviço e crie o primeiro usuário:
   ```bash
   python -m backend.scripts.create_user
   ```

### Opção B — configuração manual

1. No Render, crie um **PostgreSQL** (Free tier)
2. Crie um **Web Service** com:
   - **Runtime:** Docker
   - **Repo:** seu repositório GitHub
3. Configure as variáveis de ambiente:
   ```
   DATABASE_URL        = (Internal Database URL do banco criado)
   JWT_SECRET_KEY      = (gere uma chave forte)
   AUTH_COOKIE_SECURE  = true
   APP_TIMEZONE        = America/Sao_Paulo
   ```
4. As migrations rodam automaticamente no startup do container.

### Variáveis opcionais (e-mail, WhatsApp e push)

```
SMTP_HOST           = smtp.gmail.com
SMTP_PORT           = 587
SMTP_USE_TLS        = true
SMTP_USER           = seu@gmail.com
SMTP_PASSWORD       = sua-senha-de-app
SMTP_FROM_EMAIL     = seu@gmail.com
SMTP_FROM_NAME      = Agenda Médica
```

Para WhatsApp Cloud API, configure no ambiente de produção:

```
WHATSAPP_ACCESS_TOKEN          = token-da-meta
WHATSAPP_PHONE_NUMBER_ID       = id-do-numero-whatsapp
WHATSAPP_BUSINESS_ACCOUNT_ID   = id-da-conta-whatsapp-business
WHATSAPP_API_VERSION           = v20.0
WHATSAPP_DEFAULT_COUNTRY_CODE  = 55
WHATSAPP_TEMPLATE_LANGUAGE     = pt_BR
WHATSAPP_PATIENT_TEMPLATE_NAME = nome_do_template_paciente
WHATSAPP_DOCTOR_TEMPLATE_NAME  = nome_do_template_medico
```

Sem templates aprovados, o sistema tenta enviar texto livre pela Cloud API, útil para testes e conversas dentro da janela permitida pela Meta. Para lembretes automáticos de consulta em produção, use templates aprovados no WhatsApp Manager.

---

## Observação: senha com caracteres especiais

Se sua senha do PostgreSQL tiver caracteres especiais (`@`, `:`, espaço, acentos), você deve **URL-encodar** a senha dentro do `DATABASE_URL`:

```bash
python -c "import urllib.parse; print(urllib.parse.quote_plus('SUA_SENHA'))"
```

---

## Melhorias futuras

- Calendário semanal/mensal
- Webhook de respostas do WhatsApp
- Auditoria e logs
- Multiusuários com permissões
