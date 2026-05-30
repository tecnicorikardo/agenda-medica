"""billing checkout pro

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-30

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("acesso_ate", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "usuarios",
        sa.Column("assinatura_status", sa.String(30), nullable=False, server_default="liberado"),
    )

    op.create_table(
        "pagamentos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_reference", sa.String(80), nullable=False),
        sa.Column("meses", sa.Integer, nullable=False),
        sa.Column("valor_centavos", sa.Integer, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("mp_preference_id", sa.String(120), nullable=True),
        sa.Column("mp_payment_id", sa.String(120), nullable=True),
        sa.Column("checkout_url", sa.Text, nullable=True),
        sa.Column("pago_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_pagamentos_usuario", "pagamentos", ["usuario_id"])
    op.create_index("idx_pagamentos_external_reference", "pagamentos", ["external_reference"], unique=True)
    op.create_index("idx_pagamentos_status", "pagamentos", ["status"])
    op.create_index("idx_pagamentos_preference", "pagamentos", ["mp_preference_id"])
    op.create_index("idx_pagamentos_payment", "pagamentos", ["mp_payment_id"])


def downgrade() -> None:
    op.drop_table("pagamentos")
    op.drop_column("usuarios", "assinatura_status")
    op.drop_column("usuarios", "acesso_ate")
