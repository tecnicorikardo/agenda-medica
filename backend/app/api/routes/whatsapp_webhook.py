from __future__ import annotations

import json
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from backend.app.core.config import get_settings
from backend.app.services.whatsapp_webhook import (
    process_whatsapp_webhook,
    verify_whatsapp_signature,
)

router = APIRouter(prefix="/webhooks/whatsapp", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.get("", response_class=PlainTextResponse)
def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> PlainTextResponse:
    settings = get_settings()
    if (
        hub_mode == "subscribe"
        and settings.whatsapp_verify_token
        and hub_verify_token == settings.whatsapp_verify_token
        and hub_challenge is not None
    ):
        return PlainTextResponse(hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Falha na verificação do webhook.")


@router.post("")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict:
    settings = get_settings()
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_whatsapp_signature(raw_body, signature, settings.whatsapp_app_secret):
        raise HTTPException(status_code=403, detail="Assinatura do webhook inválida.")

    try:
        payload = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Payload JSON inválido.") from exc

    if payload.get("object") != "whatsapp_business_account":
        logger.warning("Webhook ignorado: objeto inesperado %s", payload.get("object"))
        return {"received": True}

    background_tasks.add_task(process_whatsapp_webhook, payload)
    return {"received": True}
