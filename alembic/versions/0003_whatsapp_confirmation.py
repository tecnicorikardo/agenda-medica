"""whatsapp confirmations and personalized templates

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-18

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("consultas", sa.Column("data_confirmacao", sa.DateTime(timezone=True), nullable=True))
    op.add_column("consultas", sa.Column("data_cancelamento", sa.DateTime(timezone=True), nullable=True))
    op.add_column("usuarios", sa.Column("lembrete_horas", postgresql.ARRAY(sa.Integer), nullable=True))
    op.add_column("lembretes", sa.Column("chave_idempotencia", sa.String(180), nullable=True))
    op.create_index(
        "idx_lembretes_chave_idempotencia",
        "lembretes",
        ["chave_idempotencia"],
        unique=True,
    )

    op.create_table(
        "templates_whatsapp",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "medico_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("conteudo", sa.Text, nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "tipo IN ('lembrete','confirmacao','cancelamento')",
            name="chk_templates_whatsapp_tipo",
        ),
        sa.UniqueConstraint("medico_id", "tipo", name="uq_templates_whatsapp_medico_tipo"),
    )
    op.create_index("idx_templates_whatsapp_medico", "templates_whatsapp", ["medico_id"])
    op.create_index("idx_templates_whatsapp_tipo", "templates_whatsapp", ["tipo"])

    op.create_table(
        "interacoes_whatsapp",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "medico_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "consulta_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("consultas.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "lembrete_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lembretes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event_id", sa.String(255), nullable=False),
        sa.Column("telefone", sa.String(30), nullable=True),
        sa.Column("direcao", sa.String(15), nullable=False),
        sa.Column("tipo", sa.String(40), nullable=False),
        sa.Column("acao", sa.String(30), nullable=True),
        sa.Column("status_processamento", sa.String(30), nullable=False, server_default="recebido"),
        sa.Column("erro", sa.Text, nullable=True),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("processado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_interacoes_whatsapp_event", "interacoes_whatsapp", ["event_id"], unique=True)
    op.create_index("idx_interacoes_whatsapp_medico", "interacoes_whatsapp", ["medico_id"])
    op.create_index("idx_interacoes_whatsapp_consulta", "interacoes_whatsapp", ["consulta_id"])
    op.create_index("idx_interacoes_whatsapp_lembrete", "interacoes_whatsapp", ["lembrete_id"])
    op.create_index("idx_interacoes_whatsapp_telefone", "interacoes_whatsapp", ["telefone"])


def downgrade() -> None:
    op.drop_table("interacoes_whatsapp")
    op.drop_table("templates_whatsapp")
    op.drop_index("idx_lembretes_chave_idempotencia", table_name="lembretes")
    op.drop_column("lembretes", "chave_idempotencia")
    op.drop_column("usuarios", "lembrete_horas")
    op.drop_column("consultas", "data_cancelamento")
    op.drop_column("consultas", "data_confirmacao")
