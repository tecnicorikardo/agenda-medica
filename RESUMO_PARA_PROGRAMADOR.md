# Resumo para Programador

Este arquivo e uma entrada rapida para quem vai pegar o projeto sem contexto. O guia completo fica em [`docs/GUIA_DESENVOLVEDOR.md`](docs/GUIA_DESENVOLVEDOR.md).

## O que e o sistema

Agenda Medica e uma aplicacao web para consultorio medico. Ela permite criar conta de medico, cadastrar pacientes, agendar consultas, acompanhar dashboard diario e enviar lembretes por e-mail, WhatsApp e notificacoes push.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic e PostgreSQL.
- Frontend: HTML, CSS e JavaScript puro em formato SPA/PWA.
- Deploy: Render com Docker, PostgreSQL e cron jobs.
- Idioma e fuso: portugues do Brasil, `America/Sao_Paulo`.

## Pontos de entrada do codigo

| Arquivo/pasta | Para que serve |
|---|---|
| `backend/app/main.py` | Cria o FastAPI, registra `/api`, serve assets e frontend. |
| `backend/app/api/router.py` | Centraliza o registro das rotas. |
| `backend/app/api/routes/` | Endpoints HTTP por area do produto. |
| `backend/app/models/` | Modelos/tabelas SQLAlchemy. |
| `backend/app/schemas/` | Schemas Pydantic. |
| `backend/app/services/` | E-mail, WhatsApp, push, Mercado Pago e scheduler. |
| `frontend/app.js` | SPA principal. |
| `frontend/app.css` | Estilos, responsividade e temas. |
| `alembic/versions/` | Historico de migrations. |
| `render.yaml` | Infra do Render. |

## Contas e acessos

Nao coloque senhas, tokens ou chaves no Git. O projeto ignora `.env`, `*.env`, `MINHAS_CONTAS.md`, `private_key.pem` e `public_key.pem`.

Servicos que podem precisar de acesso:

- Render: web service, banco PostgreSQL e cron jobs.
- GitHub: repositorio e deploy automatico.
- Meta WhatsApp Cloud API: token, phone number ID, WABA ID e templates aprovados.
- Resend/Brevo/SMTP: envio de e-mail.
- Mercado Pago: checkout e webhook de pagamento.

Conta do sistema: cada medico e um usuario em `usuarios`. Para criar o primeiro usuario, rode:

```bash
python -m backend.scripts.create_user
```

## Como rodar

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m backend.scripts.migrate
python -m backend.scripts.create_user
uvicorn backend.app.main:app --reload
```

Acesse `http://localhost:8000`.

## Testes principais

```bash
python -m unittest discover -s tests -p "test_*.py"
python -m compileall backend tests
```

Para E2E, consulte `docs/GUIA_DESENVOLVEDOR.md`, pois o Playwright exige servidor local e usuario de teste.

## Documentos importantes

- `docs/GUIA_DESENVOLVEDOR.md`: arquitetura, rotas, banco, deploy, scripts e troubleshooting.
- `docs/FUNCIONALIDADES.md`: comportamento funcional do produto.
- `docs/WHATSAPP_TEMPLATES.md`: templates WhatsApp.
- `docs/WHATSAPP_CONFIRMACAO.md`: fluxo de confirmacao por WhatsApp.
- `COMO_USAR.md`: comandos operacionais.
