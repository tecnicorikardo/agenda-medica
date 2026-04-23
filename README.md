# Agenda Médica (web)

Sistema web profissional para agenda médica, pensado para uso real no dia a dia (rua + consultório) e funcionando bem no celular e no desktop.

## Tecnologias

- **Frontend:** HTML/CSS/JS responsivo (SPA leve)
- **Backend:** Python + FastAPI
- **Banco:** Supabase (Postgres)
- **Deploy:** Railway (Procfile pronto)

## Estrutura do projeto

- `backend/` API, autenticação, regras de agenda, modelos e endpoints
- `frontend/` interface web responsiva
- `docs/` SQL do Supabase e documentação

## Funcionalidades (MVP funcional)

- Login/Logout com cookie HttpOnly (rotas `/api` protegidas)
- Dashboard do dia (consultas, canceladas, concluídas, próximos, horários livres)
- Agenda: criar, reagendar, cancelar, confirmar, concluir, marcar falta
- Pacientes: CRUD + busca rápida por nome/telefone
- Estrutura pronta para lembretes (tabela `lembretes`)

## Como rodar localmente

### 1) Criar tabelas no Supabase

1. Crie um projeto no Supabase
2. Abra o **SQL Editor**
3. Execute o arquivo `docs/supabase_schema.sql`

### 2) Configurar variáveis de ambiente

1. Copie `.env.example` para `.env`
2. Ajuste `DATABASE_URL` (Postgres do Supabase) e `JWT_SECRET_KEY`

### 3) Instalar dependências e executar

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Abra: `http://localhost:8000`

### 4) Criar o primeiro usuário

```bash
python backend/scripts/create_user.py
```

## Como conectar no Supabase

- Use a string Postgres do Supabase em `DATABASE_URL` (Settings → Database → Connection string).
- Recomendado: crie uma senha forte para `JWT_SECRET_KEY`.

### Observação: senha com caracteres especiais

Se sua senha do Postgres tiver caracteres especiais (ex: `@`, `:`, espaço, acentos), você deve **URL-encodar** a senha dentro do `DATABASE_URL`, senão a conexão pode falhar.

One-liner para gerar a senha encoded:

```bash
python -c "import urllib.parse; print(urllib.parse.quote_plus('SUA_SENHA'))"
```

## Deploy no Railway

1. Suba o repositório no GitHub (push feito por você)
2. No Railway, crie um novo projeto a partir do repo
3. Configure variáveis de ambiente:
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`
   - `AUTH_COOKIE_SECURE=true`
4. Railway detecta `Procfile` e usa o comando:
   - `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

Alternativa (mais previsível): use o `Dockerfile` (Railway suporta deploy por Dockerfile).

## Melhorias futuras

- Multiusuários completo (vincular pacientes/consultas por `usuario_id`)
- Constraint no Postgres para evitar conflitos no banco
- Calendário semanal/mensal
- Integração WhatsApp (webhook + templates) usando tabela `lembretes`
- Auditoria e logs
