from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    nome: Mapped[str | None] = mapped_column(String(255), nullable=True)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Perfil profissional
    crm: Mapped[str | None] = mapped_column(String(50), nullable=True)
    especialidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email_contato: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nome_clinica: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Configurações de lembrete por e-mail
    lembrete_ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    lembrete_dias: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    lembrete_msg_paciente: Mapped[str | None] = mapped_column(Text, nullable=True)
    lembrete_msg_medico: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

