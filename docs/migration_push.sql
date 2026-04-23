-- Migração: tabela de subscriptions Web Push
-- Execute no SQL Editor do Supabase

create table if not exists push_subscriptions (
  id          uuid primary key default gen_random_uuid(),
  usuario_id  uuid references usuarios(id) on delete cascade,
  endpoint    text not null unique,
  p256dh      text not null,
  auth        text not null,
  user_agent  text,
  created_at  timestamptz not null default now()
);

create index if not exists idx_push_usuario on push_subscriptions (usuario_id);
