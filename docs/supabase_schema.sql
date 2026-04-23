-- Schema inicial (Supabase Postgres)
-- Execute no SQL Editor do Supabase.

create extension if not exists pgcrypto;

-- Utilitário para updated_at
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- =========================
-- usuarios
-- =========================
create table if not exists usuarios (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  nome text,
  senha_hash text not null,
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_usuarios_updated_at on usuarios;
create trigger trg_usuarios_updated_at
before update on usuarios
for each row execute function set_updated_at();

create index if not exists idx_usuarios_email on usuarios (email);

-- =========================
-- pacientes
-- =========================
create table if not exists pacientes (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid references usuarios(id) on delete set null,
  nome_completo text not null,
  telefone text not null,
  email text,
  data_nascimento date,
  observacoes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_pacientes_updated_at on pacientes;
create trigger trg_pacientes_updated_at
before update on pacientes
for each row execute function set_updated_at();

create index if not exists idx_pacientes_nome on pacientes (nome_completo);
create index if not exists idx_pacientes_telefone on pacientes (telefone);
create index if not exists idx_pacientes_usuario on pacientes (usuario_id);

-- =========================
-- consultas
-- =========================
create table if not exists consultas (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid references usuarios(id) on delete set null,
  paciente_id uuid not null references pacientes(id) on delete restrict,
  inicio timestamptz not null,
  fim timestamptz not null,
  status text not null check (status in ('agendada','confirmada','concluida','cancelada','faltou')),
  observacoes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint chk_consultas_intervalo check (fim > inicio)
);

drop trigger if exists trg_consultas_updated_at on consultas;
create trigger trg_consultas_updated_at
before update on consultas
for each row execute function set_updated_at();

create index if not exists idx_consultas_inicio on consultas (inicio);
create index if not exists idx_consultas_status on consultas (status);
create index if not exists idx_consultas_paciente on consultas (paciente_id);
create index if not exists idx_consultas_usuario on consultas (usuario_id);

-- =========================
-- lembretes (estrutura pronta)
-- =========================
create table if not exists lembretes (
  id uuid primary key default gen_random_uuid(),
  consulta_id uuid not null references consultas(id) on delete cascade,
  canal text not null,
  agendado_para timestamptz not null,
  status text not null default 'pendente',
  enviado_em timestamptz,
  payload jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_lembretes_updated_at on lembretes;
create trigger trg_lembretes_updated_at
before update on lembretes
for each row execute function set_updated_at();

create index if not exists idx_lembretes_consulta on lembretes (consulta_id);
create index if not exists idx_lembretes_agendado_para on lembretes (agendado_para);

