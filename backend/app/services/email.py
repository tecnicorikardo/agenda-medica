"""Serviço de envio de e-mail via SMTP (aiosmtplib)."""
from __future__ import annotations

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


def _is_configured() -> bool:
    s = get_settings()
    return bool(s.smtp_host and s.smtp_user and s.smtp_password and s.smtp_from_email)


async def send_email(*, to: str, subject: str, html: str) -> bool:
    """Envia um e-mail HTML. Retorna True se enviado, False se SMTP não configurado."""
    if not _is_configured():
        logger.warning("SMTP não configurado — e-mail não enviado para %s", to)
        return False

    s = get_settings()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{s.smtp_from_name} <{s.smtp_from_email}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password,
            start_tls=s.smtp_use_tls,
        )
        logger.info("E-mail enviado para %s — %s", to, subject)
        return True
    except Exception as exc:
        logger.error("Falha ao enviar e-mail para %s: %s", to, exc)
        raise
