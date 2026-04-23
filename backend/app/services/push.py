"""Serviço de Web Push usando VAPID / pywebpush."""
from __future__ import annotations

import json
import logging

from pywebpush import webpush, WebPushException

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


def _is_configured() -> bool:
    s = get_settings()
    return bool(s.vapid_public_key and s.vapid_private_key)


def send_push(
    *,
    endpoint: str,
    p256dh: str,
    auth: str,
    title: str,
    body: str,
    url: str = "/",
    icon: str = "/icons/icon-192.png",
    badge: str = "/icons/badge-72.png",
    tag: str = "agenda-medica",
) -> bool:
    """Envia uma notificação push. Retorna True se enviado."""
    if not _is_configured():
        logger.warning("VAPID não configurado — push não enviado.")
        return False

    s = get_settings()
    payload = json.dumps({
        "title": title,
        "body": body,
        "url": url,
        "icon": icon,
        "badge": badge,
        "tag": tag,
    })

    try:
        webpush(
            subscription_info={"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}},
            data=payload,
            vapid_private_key=s.vapid_private_key,
            vapid_claims={"sub": s.vapid_mailto},
        )
        return True
    except WebPushException as exc:
        # 410 Gone = subscription expirada, deve ser removida
        if exc.response is not None and exc.response.status_code == 410:
            raise
        logger.error("Falha no push: %s", exc)
        return False


def send_push_to_subscriptions(
    db,
    *,
    usuario_id,
    title: str,
    body: str,
    url: str = "/",
    tag: str = "agenda-medica",
) -> int:
    """Envia push para todas as subscriptions de um usuário. Retorna qtd enviada."""
    from sqlalchemy import select
    from backend.app.models.push_subscription import PushSubscription

    subs = list(db.scalars(
        select(PushSubscription).where(PushSubscription.usuario_id == usuario_id)
    ).all())

    enviados = 0
    to_delete = []

    for sub in subs:
        try:
            ok = send_push(
                endpoint=sub.endpoint,
                p256dh=sub.p256dh,
                auth=sub.auth,
                title=title,
                body=body,
                url=url,
                tag=tag,
            )
            if ok:
                enviados += 1
        except Exception as exc:
            # Subscription expirada — marca para remover
            logger.info("Removendo subscription expirada: %s", sub.endpoint[:60])
            to_delete.append(sub)

    for sub in to_delete:
        db.delete(sub)
    if to_delete:
        db.commit()

    return enviados
