"""Serviço de envio via WhatsApp Cloud API."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


class WhatsAppConfigError(RuntimeError):
    """Configuração obrigatória da Cloud API ausente."""


class WhatsAppSendError(RuntimeError):
    """Falha retornada pela Cloud API."""


@dataclass(frozen=True)
class WhatsAppResult:
    message_id: str | None
    raw: dict[str, Any]


def is_whatsapp_configured() -> bool:
    settings = get_settings()
    return bool(settings.whatsapp_access_token and settings.whatsapp_phone_number_id)


def normalize_whatsapp_phone(phone: str | None) -> str | None:
    """Normaliza telefone para o formato aceito pela Cloud API, sem sinal de +."""
    settings = get_settings()
    default_country_code = re.sub(r"\D", "", settings.whatsapp_default_country_code or "55")
    digits = re.sub(r"\D", "", phone or "")

    if digits.startswith("00"):
        digits = digits[2:]

    if default_country_code and not digits.startswith(default_country_code) and len(digits) <= 11:
        digits = f"{default_country_code}{digits}"

    if len(digits) < 10 or len(digits) > 15:
        return None
    return digits


def _ensure_configured() -> None:
    if not is_whatsapp_configured():
        raise WhatsAppConfigError(
            "Defina WHATSAPP_ACCESS_TOKEN e WHATSAPP_PHONE_NUMBER_ID nas variáveis de ambiente."
        )


def _extract_error(status: int, body: str) -> str:
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return f"WhatsApp Cloud API erro {status}: {body}"

    error = data.get("error") if isinstance(data, dict) else None
    if isinstance(error, dict):
        message = error.get("message") or error.get("error_user_msg")
        error_data = error.get("error_data")
        parameter_details = error_data.get("details") if isinstance(error_data, dict) else None
        code = error.get("code")
        details = f" ({code})" if code else ""
        if message:
            suffix = f" Detalhes: {parameter_details}" if parameter_details else ""
            return f"WhatsApp Cloud API erro {status}{details}: {message}{suffix}"
    return f"WhatsApp Cloud API erro {status}: {data}"


async def _post_message(payload: dict[str, Any]) -> WhatsAppResult:
    import aiohttp

    settings = get_settings()
    url = (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            body = await resp.text()
            if 200 <= resp.status < 300:
                data = json.loads(body) if body else {}
                messages = data.get("messages") if isinstance(data, dict) else None
                message_id = messages[0].get("id") if messages else None
                logger.info("WhatsApp enviado para %s", payload.get("to"))
                return WhatsAppResult(message_id=message_id, raw=data)

            error_message = _extract_error(resp.status, body)
            logger.error(error_message)
            raise WhatsAppSendError(error_message)


async def send_whatsapp_text(*, to: str, body: str, preview_url: bool = False) -> WhatsAppResult:
    _ensure_configured()
    phone = normalize_whatsapp_phone(to)
    if not phone:
        raise ValueError("Telefone inválido para WhatsApp.")

    return await _post_message({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {
            "preview_url": preview_url,
            "body": body,
        },
    })


async def send_whatsapp_template(
    *,
    to: str,
    template_name: str,
    language_code: str,
    body_parameters: list[str] | None = None,
    quick_reply_payloads: list[str] | None = None,
) -> WhatsAppResult:
    _ensure_configured()
    phone = normalize_whatsapp_phone(to)
    if not phone:
        raise ValueError("Telefone inválido para WhatsApp.")

    template: dict[str, Any] = {
        "name": template_name,
        "language": {"code": language_code},
    }
    components: list[dict[str, Any]] = []
    if body_parameters:
        components.append({
            "type": "body",
            "parameters": [
                {"type": "text", "text": str(value)}
                for value in body_parameters
            ],
        })
    for index, payload in enumerate(quick_reply_payloads or []):
        components.append({
            "type": "button",
            "sub_type": "quick_reply",
            "index": str(index),
            "parameters": [{"type": "payload", "payload": payload}],
        })
    if components:
        template["components"] = components

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "template",
        "template": template,
    }
    
    # Log detalhado para debug
    logger.info(f"WhatsApp template payload: template={template_name}, language={language_code}, params={len(body_parameters or [])}, buttons={len(quick_reply_payloads or [])}")
    logger.debug(f"WhatsApp full payload: {payload}")
    
    return await _post_message(payload)

    return await _post_message({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "template",
        "template": template,
    })


async def send_whatsapp_message(
    *,
    to: str,
    body: str,
    template_name: str = "",
    language_code: str = "pt_BR",
    template_parameters: list[str] | None = None,
    quick_reply_payloads: list[str] | None = None,
) -> WhatsAppResult:
    if template_name:
        return await send_whatsapp_template(
            to=to,
            template_name=template_name,
            language_code=language_code,
            body_parameters=template_parameters,
            quick_reply_payloads=quick_reply_payloads,
        )
    return await send_whatsapp_text(to=to, body=body)
