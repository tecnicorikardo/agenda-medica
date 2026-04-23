from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import EmailStr, Field

from backend.app.schemas.base import APIModel


class PacienteBase(APIModel):
    nome_completo: str = Field(min_length=3, max_length=255)
    telefone: str = Field(min_length=6, max_length=50)
    email: EmailStr | None = None
    data_nascimento: date | None = None
    observacoes: str | None = None


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(APIModel):
    nome_completo: str | None = Field(default=None, min_length=3, max_length=255)
    telefone: str | None = Field(default=None, min_length=6, max_length=50)
    email: EmailStr | None = None
    data_nascimento: date | None = None
    observacoes: str | None = None


class PacienteOut(PacienteBase):
    id: uuid.UUID
    created_at: datetime


class PacienteDetail(PacienteOut):
    updated_at: datetime
