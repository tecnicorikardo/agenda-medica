from __future__ import annotations

import uuid

from pydantic import EmailStr, Field

from backend.app.schemas.base import APIModel


class LoginIn(APIModel):
    email: EmailStr
    senha: str = Field(min_length=6)


class UsuarioOut(APIModel):
    id: uuid.UUID
    email: EmailStr
    nome: str | None
    crm: str | None = None
    especialidade: str | None = None
    telefone: str | None = None
    email_contato: str | None = None
    nome_clinica: str | None = None
    avatar_url: str | None = None
    # Configurações de lembrete
    lembrete_dias: list[int] = Field(default_factory=lambda: [1])
    lembrete_ativo: bool = True
    lembrete_msg_paciente: str | None = None
    lembrete_msg_medico: str | None = None


class UsuarioPerfilUpdate(APIModel):
    nome: str | None = None
    crm: str | None = None
    especialidade: str | None = None
    telefone: str | None = None
    email_contato: str | None = None
    nome_clinica: str | None = None
    avatar_url: str | None = None
    # Configurações de lembrete
    lembrete_dias: list[int] | None = None
    lembrete_ativo: bool | None = None
    lembrete_msg_paciente: str | None = None
    lembrete_msg_medico: str | None = None


class MeOut(APIModel):
    usuario: UsuarioOut
