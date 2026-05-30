from __future__ import annotations

import calendar
import math
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.billing import Pagamento
from backend.app.models.user import Usuario
from backend.app.schemas.billing import BillingCheckoutIn, BillingCheckoutOut, BillingPlanOut, BillingStatusOut
from backend.app.services.mercadopago import MercadoPagoError, create_preference, get_payment
from backend.app.utils.deps import get_current_user

router = APIRouter(prefix="/billing")

MONTH_PRICE_CENTS = 2990
ANNUAL_PRICE_CENTS = 29990
WARNING_DAYS_AFTER_EXPIRE = 30


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _amount_for_months(months: int) -> int:
    if months == 12:
        return ANNUAL_PRICE_CENTS
    return MONTH_PRICE_CENTS * months


def _format_brl(cents: int) -> str:
    value = cents / 100
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _plans() -> list[BillingPlanOut]:
    return [
        BillingPlanOut(
            meses=months,
            valor_centavos=_amount_for_months(months),
            valor_formatado=_format_brl(_amount_for_months(months)),
            destaque=months == 12,
        )
        for months in range(1, 13)
    ]


def _add_months(base: datetime, months: int) -> datetime:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return base.replace(year=year, month=month, day=day)


def _billing_status(user: Usuario) -> BillingStatusOut:
    access_until = user.acesso_ate
    now = _now()

    if access_until is None:
        return BillingStatusOut(
            acesso_ate=None,
            status="liberado",
            bloqueado=False,
            em_aviso=False,
            planos=_plans(),
        )

    if access_until.tzinfo is None:
        access_until = access_until.replace(tzinfo=timezone.utc)

    days_remaining = math.ceil((access_until - now).total_seconds() / 86400)
    if days_remaining >= 0:
        return BillingStatusOut(
            acesso_ate=access_until,
            status="ativo",
            bloqueado=False,
            em_aviso=False,
            dias_restantes=days_remaining,
            planos=_plans(),
        )

    block_at = access_until + timedelta(days=WARNING_DAYS_AFTER_EXPIRE)
    days_to_block = math.ceil((block_at - now).total_seconds() / 86400)
    blocked = days_to_block < 0
    return BillingStatusOut(
        acesso_ate=access_until,
        status="bloqueado" if blocked else "vencido_aviso",
        bloqueado=blocked,
        em_aviso=not blocked,
        dias_restantes=days_remaining,
        dias_para_bloqueio=max(days_to_block, 0),
        planos=_plans(),
    )


def _base_url(request: Request) -> str:
    settings = get_settings()
    base = settings.public_base_url.strip() or str(request.base_url)
    return base.rstrip("/")


@router.get("/status", response_model=BillingStatusOut)
def status(user: Usuario = Depends(get_current_user)) -> BillingStatusOut:
    return _billing_status(user)


@router.post("/checkout", response_model=BillingCheckoutOut)
def checkout(
    data: BillingCheckoutIn,
    request: Request,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> BillingCheckoutOut:
    settings = get_settings()
    if not settings.mercadopago_access_token:
        raise HTTPException(status_code=500, detail="Mercado Pago nÃ£o configurado.")

    amount_cents = _amount_for_months(data.meses)
    external_reference = f"pag-{uuid.uuid4().hex}"
    base_url = _base_url(request)
    title = f"Agenda MÃ©dica - {data.meses} {'mÃªs' if data.meses == 1 else 'meses'}"

    payment = Pagamento(
        usuario_id=user.id,
        external_reference=external_reference,
        meses=data.meses,
        valor_centavos=amount_cents,
        status="pending",
    )
    db.add(payment)
    db.flush()

    payload = {
        "items": [
            {
                "id": f"agenda-medica-{data.meses}m",
                "title": title,
                "description": f"Acesso ao sistema por {data.meses} {'mÃªs' if data.meses == 1 else 'meses'}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": amount_cents / 100,
            }
        ],
        "payer": {"email": user.email, "name": user.nome or ""},
        "external_reference": external_reference,
        "notification_url": f"{base_url}/api/billing/webhook",
        "back_urls": {
            "success": f"{base_url}/#/pagamento?status=success",
            "pending": f"{base_url}/#/pagamento?status=pending",
            "failure": f"{base_url}/#/pagamento?status=failure",
        },
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "credit_card"},
                {"id": "debit_card"},
                {"id": "ticket"},
                {"id": "atm"},
            ],
            "installments": 1,
        },
        "statement_descriptor": "AGENDA MEDICA",
    }

    try:
        preference = create_preference(settings.mercadopago_access_token, payload)
    except MercadoPagoError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    checkout_url = preference.get("init_point") or preference.get("sandbox_init_point")
    if not checkout_url:
        db.rollback()
        raise HTTPException(status_code=502, detail="Mercado Pago nÃ£o retornou URL de pagamento.")

    payment.mp_preference_id = preference.get("id")
    payment.checkout_url = checkout_url
    payment.payload = {"preference": preference}
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return BillingCheckoutOut(
        pagamento_id=str(payment.id),
        preference_id=payment.mp_preference_id or "",
        checkout_url=payment.checkout_url or checkout_url,
    )


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    settings = get_settings()
    if not settings.mercadopago_access_token:
        return {"ok": True}

    try:
        body = await request.json()
    except Exception:
        body = {}

    payment_id = (
        request.query_params.get("id")
        or request.query_params.get("data.id")
        or body.get("id")
        or (body.get("data") or {}).get("id")
    )
    resource = request.query_params.get("resource") or body.get("resource")
    if not payment_id and resource and "/payments/" in str(resource):
        payment_id = str(resource).rstrip("/").split("/")[-1]
    topic = request.query_params.get("topic") or request.query_params.get("type") or body.get("type")
    if topic and topic not in {"payment", "payments"}:
        return {"ok": True}
    if not payment_id:
        return {"ok": True}

    try:
        mp_payment = get_payment(settings.mercadopago_access_token, str(payment_id))
    except MercadoPagoError:
        return {"ok": True}

    external_reference = mp_payment.get("external_reference")
    if not external_reference:
        return {"ok": True}

    payment = db.query(Pagamento).filter(Pagamento.external_reference == external_reference).first()
    if not payment:
        return {"ok": True}

    payment.mp_payment_id = str(mp_payment.get("id") or payment_id)
    payment.status = mp_payment.get("status") or payment.status
    payment.payload = {"payment": mp_payment, "webhook": body}

    if payment.status == "approved" and payment.pago_em is None:
        now = _now()
        user = db.query(Usuario).filter(Usuario.id == payment.usuario_id).first()
        if user:
            current_until = user.acesso_ate
            if current_until and current_until.tzinfo is None:
                current_until = current_until.replace(tzinfo=timezone.utc)
            base = current_until if current_until and current_until > now else now
            user.acesso_ate = _add_months(base, payment.meses)
            user.assinatura_status = "ativo"
            db.add(user)
        payment.pago_em = now

    db.add(payment)
    db.commit()
    return {"ok": True}
