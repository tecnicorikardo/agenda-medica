from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class InteracaoWhatsApp(Base):
    __tablename__ = "interacoes_whatsapp"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medico_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    consulta_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    lembrete_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lembretes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    direcao: Mapped[str] = mapped_column(String(15), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    acao: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status_processamento: Mapped[str] = mapped_column(String(30), nullable=False, server_default="recebido")
    erro: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
