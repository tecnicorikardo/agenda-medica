from __future__ import annotations

from datetime import datetime

from pydantic import Field

from backend.app.schemas.base import APIModel


class BillingCheckoutIn(APIModel):
    meses: int = Field(ge=1, le=12)


class BillingPlanOut(APIModel):
    meses: int
    valor_centavos: int
    valor_formatado: str
    destaque: bool = False


class BillingStatusOut(APIModel):
    acesso_ate: datetime | None = None
    status: str
    bloqueado: bool
    em_aviso: bool
    dias_restantes: int | None = None
    dias_para_bloqueio: int | None = None
    planos: list[BillingPlanOut]


class BillingCheckoutOut(APIModel):
    pagamento_id: str
    preference_id: str
    checkout_url: str
