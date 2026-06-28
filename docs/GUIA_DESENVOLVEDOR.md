# Guia do Desenvolvedor - Agenda Medica

Ultima atualizacao: 2026-06-28

Este documento e o ponto de partida para outro programador entender, rodar, manter e publicar o sistema. Ele evita credenciais reais de proposito: contas, senhas, tokens e chaves devem ficar no painel dos servicos externos, no `.env` local ou em `MINHAS_CONTAS.md`, que e ignorado pelo Git.

## Visao geral

Agenda Medica e uma aplicacao web para gestao de consultorio medico. O medico cria conta, cadastra pacientes, agenda consultas, acompanha indicadores do dia e envia lembretes por e-mail, WhatsApp e notificacoes push.

Dados principais:

| Item | Informacao |
|---|---|
| Idioma do produto | Portugues do Brasil |
| Fuso horario padrao | `America/Sao_Paulo` |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| Frontend | HTML, CSS e JavaScript puro em SPA leve |
| Banco de dados | PostgreSQL |
| Deploy atual | Render com Docker |
| URL publica configurada | `https://agenda-medica-2c9b.onrender.com` |
| Branch principal | `main` |

## Contas, acessos e segredos

Nao coloque credenciais reais em arquivos versionados. O projeto ja ignora `.env`, `*.env`, `MINHAS_CONTAS.md`, `private_key.pem` e `public_key.pem`.

Use este mapa para saber onde cada acesso normalmente fica:

| Assunto | Onde configurar | Observacoes |
|---|---|---|
| Conta do sistema | Tela de cadastro ou `python -m backend.scripts.create_user` | Cada medico e um registro em `usuarios`. |
| Banco PostgreSQL | `DATABASE_URL` no `.env` ou Render Environment | Em producao, use a Internal Database URL do Render. |
| JWT/cookie | `JWT_SECRET_KEY` e variaveis `AUTH_COOKIE_*` | Gere uma chave forte e mantenha fora do Git. |
| Render | Dashboard do Render | O `render.yaml` define web service, banco e cron jobs, mas segredos ficam com `sync: false`. |
| GitHub | Repositorio remoto | Push em `main` dispara redeploy quando integrado ao Render. |
| E-mail | `RESEND_API_KEY`, `BREVO_API_KEY` ou SMTP | A ordem do codigo e Resend, Brevo, SMTP. |
| WhatsApp Cloud API | Variaveis `WHATSAPP_*` no ambiente | Templates aprovados pela Meta sao obrigatorios para mensagens proativas. |
| Web Push | `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_MAILTO` | Gere com `python -m backend.scripts.gen_vapid`. |
| Mercado Pago | `MERCADOPAGO_ACCESS_TOKEN` | Usado pelo modulo de cobranca/checkout. |

Conta de teste E2E: os testes Playwright usam `TEST_EMAIL` e `TEST_PASSWORD` quando definidos. Se nao existirem, ha fallback em `tests/e2e/create_test_user.py` e `tests/e2e/helpers/auth.js`. Use isso apenas em ambiente local ou de teste.

## Arquitetura

O FastAPI sobe a API em `/api` e tambem serve o frontend estatico da pasta `frontend/` na raiz. Assim, em desenvolvimento e producao, a mesma origem pode entregar a SPA e os endpoints.

Fluxo principal:

```text
Navegador/PWA
  -> frontend/index.html, app.js, app.css
  -> chamadas fetch para /api/*
  -> FastAPI
  -> SQLAlchemy Session
  -> PostgreSQL
```

Responsabilidades por pasta:

| Pasta/arquivo | Responsabilidade |
|---|---|
| `backend/app/main.py` | Cria o app FastAPI, registra rotas, CORS, assets e frontend estatico. |
| `backend/app/api/router.py` | Agrega todas as rotas sob `/api`. |
| `backend/app/api/routes/` | Endpoints HTTP por dominio. |
| `backend/app/core/` | Configuracao por ambiente e seguranca. |
| `backend/app/crud/` | Consultas reutilizaveis ao banco. |
| `backend/app/db/` | Engine, `SessionLocal` e base declarativa. |
| `backend/app/models/` | Modelos SQLAlchemy. |
| `backend/app/schemas/` | Schemas Pydantic de entrada/saida. |
| `backend/app/services/` | Integracoes e regras de servico: e-mail, push, WhatsApp, Mercado Pago, scheduler. |
| `backend/app/utils/` | Dependencias compartilhadas e geracao de PDF. |
| `backend/scripts/` | Scripts operacionais e de manutencao. |
| `alembic/` | Migrations do banco. |
| `frontend/` | SPA, PWA manifest, service worker e icones. |
| `tests/` | Testes unitarios Python e testes E2E Playwright. |
| `docs/` | Documentacao tecnica e scripts SQL historicos. |

## Backend

Configuracao:

- `backend/app/core/config.py` usa `pydantic-settings`.
- O arquivo `.env` local e carregado automaticamente.
- Variaveis desconhecidas sao ignoradas para permitir ambientes com configuracoes extras.

Autenticacao:

- Login por e-mail e senha.
- Senha com hash via `passlib`/`bcrypt`.
- Sessao em JWT armazenado em cookie HttpOnly.
- `backend/app/utils/deps.py` centraliza a dependencia de usuario autenticado.

Lembretes e tarefas automaticas:

- `backend/app/services/scheduler.py` agenda lembretes diarios e confirmacoes WhatsApp quando `SCHEDULER_ENABLED=true`.
- No Render, o web service esta configurado com `SCHEDULER_ENABLED=false`.
- Em producao, os disparos ficam nos cron jobs do `render.yaml`.

Servicos externos:

- `backend/app/services/email.py`: tenta Resend, depois Brevo, depois SMTP.
- `backend/app/services/whatsapp.py`: envia texto livre ou template pela Meta Cloud API.
- `backend/app/services/whatsapp_webhook.py`: processa respostas e status recebidos por webhook.
- `backend/app/services/push.py`: envia Web Push quando VAPID esta configurado.
- `backend/app/services/mercadopago.py`: integra Checkout Pro e consulta pagamentos.

## Frontend

A interface fica em `frontend/app.js` e `frontend/app.css`. O app e uma SPA sem framework, com navegacao por hash, telas responsivas e suporte a PWA.

Arquivos principais:

| Arquivo | Funcao |
|---|---|
| `frontend/index.html` | HTML base da SPA. |
| `frontend/app.js` | Estado da aplicacao, chamadas API, navegacao e interacoes. |
| `frontend/app.css` | Layout, temas, responsividade e estados visuais. |
| `frontend/sw.js` | Service worker para cache/PWA. |
| `frontend/manifest.json` | Manifest de instalacao PWA. |
| `frontend/icons/` | Icones usados pelo PWA e pela interface. |

## Banco de dados

O banco e PostgreSQL e as alteracoes estruturais devem passar por Alembic.

Tabelas principais:

| Tabela | Modelo | Finalidade |
|---|---|---|
| `usuarios` | `Usuario` | Medicos, login, perfil profissional, configuracoes de lembrete e acesso comercial. |
| `pacientes` | `Paciente` | Pacientes vinculados ao medico. |
| `consultas` | `Consulta` | Agendamentos, horarios, status e observacoes. |
| `lembretes` | `Lembrete` | Controle de envios e idempotencia de lembretes. |
| `push_subscriptions` | `PushSubscription` | Dispositivos autorizados para Web Push. |
| `pagamentos` | `Pagamento` | Controle de checkout e pagamentos Mercado Pago. |
| `templates_whatsapp` | `TemplateWhatsApp` | Templates personalizados por medico. |
| `interacoes_whatsapp` | `InteracaoWhatsApp` | Eventos recebidos/enviados via WhatsApp e status de processamento. |

Comandos:

```bash
python -m backend.scripts.migrate
alembic revision -m "descricao_da_migration"
alembic upgrade head
```

## Rotas da API

Todas as rotas abaixo recebem o prefixo `/api`.

| Dominio | Rotas principais |
|---|---|
| Saude | `GET /health`, `GET /health/db` |
| Auth | `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `POST /auth/cadastro`, `POST /auth/esqueci-senha`, `POST /auth/alterar-senha`, `PUT /auth/perfil`, `POST /auth/perfil/avatar`, `DELETE /auth/perfil/avatar`, `POST /auth/reset-direto` |
| Dashboard | `GET /dashboard` |
| Pacientes | `GET /patients`, `POST /patients`, `GET /patients/{id}`, `PUT /patients/{id}`, `DELETE /patients/{id}`, `GET /patients/{id}/history`, `GET /patients/{id}/history/pdf`, `GET /patients/export/excel`, `POST /patients/import/excel` |
| Consultas | `GET /appointments`, `GET /appointments/range`, `GET /appointments/upcoming`, `POST /appointments`, `PUT /appointments/{id}`, `POST /appointments/{id}/cancel`, `POST /appointments/{id}/status/{status}` |
| Cobranca | `GET /billing/status`, `POST /billing/checkout`, `POST /billing/webhook` |
| Push | `GET /push/vapid-public-key`, `POST /push/subscribe`, `POST /push/unsubscribe`, `POST /push/test` |
| E-mail | `POST /email/test` |
| WhatsApp | `POST /whatsapp/test`, `GET /whatsapp/templates`, `PUT /whatsapp/templates/{tipo}`, `POST /whatsapp/templates/{tipo}/reset`, `POST /whatsapp/templates/preview`, `GET /webhooks/whatsapp`, `POST /webhooks/whatsapp` |

## Variaveis de ambiente

Minimo para rodar local:

```env
APP_NAME="Agenda Medica"
ENV=development
APP_TIMEZONE="America/Sao_Paulo"
DATABASE_URL="postgresql://postgres:senha@localhost:5432/agenda_medica"
JWT_SECRET_KEY="gere-uma-chave-forte"
AUTH_COOKIE_SECURE=false
```

Variaveis opcionais ou de producao:

| Variavel | Uso |
|---|---|
| `APP_PUBLIC_URL` | URL publica usada em links enviados por e-mail/mensagens. |
| `SCHEDULER_ENABLED` | Liga/desliga o scheduler interno do FastAPI. |
| `CORS_ORIGINS` | Libera origens externas em desenvolvimento. |
| `RESEND_API_KEY` | Envio de e-mail via Resend. |
| `BREVO_API_KEY` | Envio de e-mail via Brevo. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USE_TLS`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME` | Envio por SMTP. |
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_MAILTO` | Web Push. |
| `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID` | Meta WhatsApp Cloud API. |
| `WHATSAPP_API_VERSION`, `WHATSAPP_DEFAULT_COUNTRY_CODE`, `WHATSAPP_TEMPLATE_LANGUAGE` | Ajustes da API do WhatsApp. |
| `WHATSAPP_PATIENT_TEMPLATE_NAME`, `WHATSAPP_DOCTOR_TEMPLATE_NAME` | Templates aprovados pela Meta. |
| `WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE`, `WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT` | Formato dos parametros e botoes do template de paciente. |
| `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET` | Verificacao e assinatura do webhook WhatsApp. |
| `MERCADOPAGO_ACCESS_TOKEN` | Checkout Mercado Pago. |

Use `.env.example` como base e preencha valores reais fora do Git.

## Rodando localmente

1. Suba um PostgreSQL:

```bash
docker run -d --name agenda-db -e POSTGRES_PASSWORD=senha -e POSTGRES_DB=agenda_medica -p 5432:5432 postgres:16
```

2. Crie e ative o ambiente Python:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure o ambiente:

```bash
copy .env.example .env
```

4. Rode migrations e crie usuario:

```bash
python -m backend.scripts.migrate
python -m backend.scripts.create_user
```

5. Inicie o servidor:

```bash
uvicorn backend.app.main:app --reload
```

Acesse `http://localhost:8000`.

## Deploy no Render

O deploy usa Docker.

- `Dockerfile` instala dependencias, copia backend, frontend, assets e inicia com migrations.
- `render.yaml` define:
  - `agenda-medica`: web service Docker.
  - `agenda-medica-db`: PostgreSQL.
  - `agenda-medica-lembretes`: cron diario para e-mail/WhatsApp/push de D+1 e D+2.
  - `agenda-medica-whatsapp-confirmacoes`: cron a cada 10 minutos para confirmacoes WhatsApp.

No Render, mantenha segredos como `sync: false` e preencha pelo dashboard. O web service roda migrations no startup:

```bash
python -m backend.scripts.migrate && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

## Scripts uteis

| Comando | Uso |
|---|---|
| `python -m backend.scripts.migrate` | Aplica migrations. |
| `python -m backend.scripts.create_user` | Cria o primeiro medico. |
| `python -m backend.scripts.reset_password` | Auxilia recuperacao manual de senha. |
| `python -m backend.scripts.seed_data` | Gera dados de exemplo. |
| `python -m backend.scripts.gen_vapid` | Gera chaves Web Push. |
| `python -m backend.scripts.send_email_reminders --dias 1 --dias 2` | Dispara lembretes manualmente. |
| `python -m backend.scripts.send_whatsapp_reminders` | Processa confirmacoes WhatsApp. |
| `python -m backend.scripts.check_whatsapp_templates` | Verifica templates no Meta. |
| `python tests/e2e/create_test_user.py` | Cria/atualiza usuario usado nos E2E. |

## Testes e verificacoes

Testes unitarios Python:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Compilacao sintatica Python:

```bash
python -m compileall backend tests
```

Testes E2E:

```bash
cd tests/e2e
npm install
python create_test_user.py
npx playwright test
```

Antes dos E2E, o servidor precisa estar em `http://localhost:8000` e o banco precisa conter o usuario de teste.

## Regras para manutencao

- Preserve a separacao entre rotas, schemas, modelos, CRUD e services.
- Nao duplique regras de negocio no frontend quando elas pertencem ao backend.
- Toda mudanca de banco deve ter migration Alembic.
- Nao grave tokens, senhas, chaves privadas ou URLs com senha em arquivos versionados.
- Ao alterar WhatsApp, revise tambem `docs/WHATSAPP_TEMPLATES.md` e `docs/WHATSAPP_CONFIRMACAO.md`.
- Ao alterar comportamento de lembretes, rode os testes Python e confira idempotencia em `lembretes`.
- Ao alterar UI, valide pelo menos mobile e desktop, pois o produto e usado em celular.

## Solucao de problemas comuns

| Sintoma | Causa provavel | Acao |
|---|---|---|
| `DATABASE_URL` nao definido | `.env` ausente ou variavel vazia | Copie `.env.example` e configure a string do Postgres. |
| Erro de senha no Postgres | Senha com caracteres especiais sem URL encoding | Encode a senha antes de montar `DATABASE_URL`. |
| Login nao persiste em producao | Cookie inseguro ou dominio incorreto | Verifique `AUTH_COOKIE_SECURE`, `AUTH_COOKIE_SAMESITE` e `AUTH_COOKIE_DOMAIN`. |
| E-mail nao envia no Render | SMTP bloqueado ou credenciais ausentes | Prefira Resend/Brevo ou revise variaveis SMTP. |
| WhatsApp retorna sucesso mas paciente nao recebe | Mensagem livre fora da janela de 24h | Use template aprovado pela Meta. |
| Template WhatsApp da erro de parametros | Ordem/quantidade diferente do template aprovado | Rode `python -m backend.scripts.check_whatsapp_templates` e revise `WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE`. |
| Push nao funciona | VAPID ausente ou permissao negada no navegador | Gere chaves VAPID e reinscreva o dispositivo. |
