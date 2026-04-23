"""Rotas de Web Push — subscribe, unsubscribe, vapid-public-key."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.push_subscription import PushSubscription
from backend.app.utils.deps import get_current_user

router = APIRouter(prefix="/push", tags=["push"])


@router.get("/vapid-public-key")
def vapid_public_key() -> dict:
    """Retorna a chave pública VAPID para o frontend."""
    return {"publicKey": get_settings().vapid_public_key}


@router.post("/subscribe")
def subscribe(
    data: dict,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> dict:
    """Salva ou atualiza uma subscription de push do browser."""
    endpoint = data.get("endpoint", "")
    keys = data.get("keys", {})
    p256dh = keys.get("p256dh", "")
    auth = keys.get("auth", "")

    if not endpoint or not p256dh or not auth:
        return {"ok": False, "detail": "Dados incompletos"}

    ua = request.headers.get("user-agent", "")[:255]

    # Upsert por endpoint
    existing = db.scalar(
        select(PushSubscription).where(PushSubscription.endpoint == endpoint)
    )
    if existing:
        existing.usuario_id = user.id
        existing.p256dh = p256dh
        existing.auth = auth
        existing.user_agent = ua
        db.add(existing)
    else:
        db.add(PushSubscription(
            usuario_id=user.id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=ua,
        ))
    db.commit()
    return {"ok": True}


@router.post("/unsubscribe")
def unsubscribe(
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> dict:
    """Remove uma subscription."""
    endpoint = data.get("endpoint", "")
    db.execute(
        delete(PushSubscription).where(
            PushSubscription.endpoint == endpoint,
            PushSubscription.usuario_id == user.id,
        )
    )
    db.commit()
    return {"ok": True}


@router.post("/test")
def test_push(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> dict:
    """Envia uma notificação de teste para o usuário logado."""
    from backend.app.services.push import send_push_to_subscriptions
    n = send_push_to_subscriptions(
        db,
        usuario_id=user.id,
        title="🏥 Agenda Médica",
        body="Notificações push funcionando!",
        url="/",
        tag="test",
    )
    return {"ok": True, "enviados": n}
