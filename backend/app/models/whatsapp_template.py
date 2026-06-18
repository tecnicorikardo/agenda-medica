from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class TemplateWhatsApp(Base):
    __tablename__ = "templates_whatsapp"
    __table_args__ = (
        UniqueConstraint("medico_id", "tipo", name="uq_templates_whatsapp_medico_tipo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medico_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
