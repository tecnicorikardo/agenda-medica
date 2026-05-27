"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-26

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── usuarios ──────────────────────────────────────────────────────────────
    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("nome", sa.String(255), nullable=True),
        sa.Column("senha_hash", sa.Text, nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        # Perfil profissional
        sa.Column("crm", sa.String(50), nullable=True),
        sa.Column("especialidade", sa.String(100), nullable=True),
        sa.Column("telefone", sa.String(50), nullable=True),
        sa.Column("email_contato", sa.String(255), nullable=True),
        sa.Column("nome_clinica", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        # Configurações de lembrete
        sa.Column("lembrete_ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("lembrete_dias", postgresql.ARRAY(sa.Integer), nullable=True),
        sa.Column("lembrete_msg_paciente", sa.Text, nullable=True),
        sa.Column("lembrete_msg_medico", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_usuarios_email", "usuarios", ["email"], unique=True)

    # ── pacientes ─────────────────────────────────────────────────────────────
    op.create_table(
        "pacientes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nome_completo", sa.String(255), nullable=False),
        sa.Column("telefone", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("data_nascimento", sa.Date, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_pacientes_nome", "pacientes", ["nome_completo"])
    op.create_index("idx_pacientes_telefone", "pacientes", ["telefone"])
    op.create_index("idx_pacientes_usuario", "pacientes", ["usuario_id"])

    # ── consultas ─────────────────────────────────────────────────────────────
    op.create_table(
        "consultas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pacientes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fim", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("fim > inicio", name="chk_consultas_intervalo"),
        sa.CheckConstraint(
            "status IN ('agendada','confirmada','concluida','cancelada','faltou')",
            name="chk_consultas_status",
        ),
    )
    op.create_index("idx_consultas_inicio", "consultas", ["inicio"])
    op.create_index("idx_consultas_status", "consultas", ["status"])
    op.create_index("idx_consultas_paciente", "consultas", ["paciente_id"])
    op.create_index("idx_consultas_usuario", "consultas", ["usuario_id"])

    # ── lembretes ─────────────────────────────────────────────────────────────
    op.create_table(
        "lembretes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("consulta_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("canal", sa.String(20), nullable=False),
        sa.Column("agendado_para", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_lembretes_consulta", "lembretes", ["consulta_id"])
    op.create_index("idx_lembretes_agendado_para", "lembretes", ["agendado_para"])
    op.create_index("idx_lembretes_canal", "lembretes", ["canal"])
    op.create_index("idx_lembretes_status", "lembretes", ["status"])

    # ── push_subscriptions ────────────────────────────────────────────────────
    op.create_table(
        "push_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True),
        sa.Column("endpoint", sa.Text, nullable=False, unique=True),
        sa.Column("p256dh", sa.Text, nullable=False),
        sa.Column("auth", sa.Text, nullable=False),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_push_usuario", "push_subscriptions", ["usuario_id"])


def downgrade() -> None:
    op.drop_table("push_subscriptions")
    op.drop_table("lembretes")
    op.drop_table("consultas")
    op.drop_table("pacientes")
    op.drop_table("usuarios")
