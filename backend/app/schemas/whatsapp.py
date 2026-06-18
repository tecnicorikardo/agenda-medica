from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from backend.app.schemas.base import APIModel

TipoTemplateWhatsApp = Literal["lembrete", "confirmacao", "cancelamento"]


class WhatsAppTemplateUpdate(APIModel):
    nome: str | None = Field(default=None, max_length=120)
    conteudo: str = Field(min_length=1, max_length=4096)
    ativo: bool = True


class WhatsAppTemplatePreview(APIModel):
    tipo: TipoTemplateWhatsApp
    conteudo: str = Field(min_length=1, max_length=4096)


class WhatsAppTemplateOut(APIModel):
    id: uuid.UUID | None = None
    medico_id: uuid.UUID
    nome: str
    tipo: TipoTemplateWhatsApp
    conteudo: str
    ativo: bool
    padrao: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WhatsAppTemplatePreviewOut(APIModel):
    conteudo: str
