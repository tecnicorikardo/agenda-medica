from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from backend.app.schemas.base import APIModel

StatusConsulta = Literal["agendada", "confirmada", "concluida", "cancelada", "faltou"]


class ConsultaBase(APIModel):
    paciente_id: uuid.UUID
    inicio: datetime
    fim: datetime
    status: StatusConsulta = "agendada"
    observacoes: str | None = None


class ConsultaCreate(ConsultaBase):
    pass


class ConsultaUpdate(APIModel):
    inicio: datetime | None = None
    fim: datetime | None = None
    status: StatusConsulta | None = None
    observacoes: str | None = None


class ConsultaOut(ConsultaBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConsultaWithPaciente(ConsultaOut):
    paciente_nome: str = Field(alias="paciente_nome")
    paciente_telefone: str = Field(alias="paciente_telefone")
