"""Serviço de envio de e-mail.

Prioridade:
1. Resend API  (RESEND_API_KEY configurado)
2. Brevo API   (BREVO_API_KEY configurado)
3. SMTP direto (funciona em desenvolvimento local)
"""
from __future__ import annotations

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


def _resend_configured() -> bool:
    s = get_settings()
    return bool(getattr(s, "resend_api_key", None))


def _brevo_configured() -> bool:
    s = get_settings()
    return bool(getattr(s, "brevo_api_key", None))


def _smtp_configured() -> bool:
    s = get_settings()
    return bool(s.smtp_host and s.smtp_user and s.smtp_password and s.smtp_from_email)


async def _send_via_resend(*, to: str, subject: str, html: str) -> bool:
    """Envia via Resend API (HTTPS — funciona em qualquer cloud)."""
    import aiohttp
    s = get_settings()

    from_email = s.smtp_from_email or "onboarding@resend.dev"
    from_name  = s.smtp_from_name  or "Agenda Médica"

    payload = {
        "from": f"{from_name} <{from_email}>",
        "to": [to],
        "subject": subject,
        "html": html,
    }
    headers = {
        "Authorization": f"Bearer {s.resend_api_key}",
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.resend.com/emails", json=payload, headers=headers) as resp:
            if resp.status in (200, 201):
                logger.info("E-mail enviado via Resend para %s", to)
                return True
            body = await resp.text()
            logger.error("Resend erro %s: %s", resp.status, body)
            raise Exception(f"Resend API error {resp.status}: {body}")


async def _send_via_brevo(*, to: str, subject: str, html: str) -> bool:
    """Envia via Brevo Transactional Email API (HTTPS — sem bloqueio de porta)."""
    import aiohttp
    s = get_settings()

    from_email = s.smtp_from_email or "noreply@agenda-medica.app"
    from_name  = s.smtp_from_name  or "Agenda Médica"

    payload = {
        "sender":      {"name": from_name, "email": from_email},
        "to":          [{"email": to}],
        "subject":     subject,
        "htmlContent": html,
    }
    headers = {
        "api-key":      s.brevo_api_key,
        "Content-Type": "application/json",
        "Accept":       "application/json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
        ) as resp:
            if resp.status in (200, 201):
                logger.info("E-mail enviado via Brevo para %s", to)
                return True
            body = await resp.text()
            logger.error("Brevo erro %s: %s", resp.status, body)
            raise Exception(f"Brevo API error {resp.status}: {body}")


async def _send_via_smtp(*, to: str, subject: str, html: str) -> bool:
    """Envia via SMTP direto (para uso local)."""
    import aiosmtplib
    s = get_settings()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{s.smtp_from_name} <{s.smtp_from_email}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    await aiosmtplib.send(
        msg,
        hostname=s.smtp_host,
        port=s.smtp_port,
        username=s.smtp_user,
        password=s.smtp_password,
        start_tls=s.smtp_use_tls,
        timeout=15,
    )
    logger.info("E-mail enviado via SMTP para %s", to)
    return True


async def send_email(*, to: str, subject: str, html: str) -> bool:
    """Envia e-mail. Tenta Resend → Brevo → SMTP."""
    if _resend_configured():
        return await _send_via_resend(to=to, subject=subject, html=html)

    if _brevo_configured():
        return await _send_via_brevo(to=to, subject=subject, html=html)

    if _smtp_configured():
        return await _send_via_smtp(to=to, subject=subject, html=html)

    logger.warning("Nenhum serviço de e-mail configurado — não enviado para %s", to)
    return False
