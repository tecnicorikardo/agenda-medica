-- Migração: adiciona campos de configuração de lembretes à tabela usuarios
-- Execute no SQL Editor do Supabase (ou psql)

alter table usuarios
  add column if not exists lembrete_ativo     boolean not null default true,
  add column if not exists lembrete_dias      integer[],
  add column if not exists lembrete_msg_paciente text,
  add column if not exists lembrete_msg_medico   text;

-- Valor padrão: lembrar 1 dia antes
update usuarios set lembrete_dias = '{1}' where lembrete_dias is null;
