-- Migração: adiciona campos de perfil à tabela usuarios
-- Execute no SQL Editor do Supabase

alter table usuarios
  add column if not exists crm text,
  add column if not exists especialidade text,
  add column if not exists telefone text,
  add column if not exists email_contato text,
  add column if not exists nome_clinica text,
  add column if not exists avatar_url text;
