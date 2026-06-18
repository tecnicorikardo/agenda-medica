"""
Scheduler de tarefas automáticas — roda dentro do processo uvicorn.

Tarefas agendadas:
  - 08:00 (America/Sao_Paulo) → envia lembretes por e-mail, WhatsApp e push
    para consultas de amanhã (e/ou em 2 dias, conforme config de cada médico).

O scheduler usa APScheduler com AsyncIOScheduler para não bloquear
o event loop do FastAPI.
"""
from __future__ import annotations

import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _job_lembretes() -> None:
    """Executa o envio de lembretes para os próximos dias."""
    logger.info("[Scheduler] Iniciando envio de lembretes...")
    try:
        # Importa aqui para evitar import circular no startup
        from backend.scripts.send_email_reminders import _processar

        # Dispara para 1 e 2 dias à frente (o filtro real é feito por médico no banco)
        for dias in [1, 2]:
            stats = await _processar(dias)
            logger.info(
                (
                    "[Scheduler] %d dia(s) — e-mail pacientes: %d enviados, %d pulados, %d erros | "
                    "e-mail médicos: %d | WhatsApp médicos: %d"
                ),
                dias,
                stats.get("pacientes", 0),
                stats.get("skip", 0),
                stats.get("erros", 0),
                stats.get("medicos", 0),
                stats.get("whatsapp_medicos", 0),
            )
    except Exception as exc:
        logger.exception("[Scheduler] Erro ao enviar lembretes: %s", exc)


async def _job_whatsapp_confirmacoes() -> None:
    logger.info("[Scheduler] Iniciando lembretes de confirmação por WhatsApp...")
    try:
        from backend.app.db.session import SessionLocal
        from backend.app.services.whatsapp_reminders import process_automatic_whatsapp_reminders

        with SessionLocal() as db:
            stats = await process_automatic_whatsapp_reminders(db)
        logger.info(
            "[Scheduler] WhatsApp — %d enviados, %d ignorados, %d erros",
            stats["enviados"],
            stats["ignorados"],
            stats["erros"],
        )
    except Exception as exc:
        logger.exception("[Scheduler] Erro nos lembretes de confirmação WhatsApp: %s", exc)


def start_scheduler() -> AsyncIOScheduler:
    """Cria e inicia o scheduler. Chamado no lifespan do FastAPI."""
    global _scheduler

    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone)

    _scheduler = AsyncIOScheduler(timezone=tz)

    # Todo dia às 08:00 no fuso do app (America/Sao_Paulo por padrão)
    _scheduler.add_job(
        _job_lembretes,
        trigger=CronTrigger(hour=8, minute=0, timezone=tz),
        id="lembretes_diarios",
        name="Lembretes diários",
        replace_existing=True,
        misfire_grace_time=3600,  # tolera até 1h de atraso (ex: restart do servidor)
    )

    _scheduler.add_job(
        _job_whatsapp_confirmacoes,
        trigger=IntervalTrigger(minutes=10, timezone=tz),
        id="whatsapp_confirmacoes",
        name="Confirmações de consulta por WhatsApp",
        replace_existing=True,
        misfire_grace_time=600,
    )

    _scheduler.start()
    logger.info(
        "[Scheduler] Iniciado — lembretes agendados para 08:00 (%s)",
        settings.app_timezone,
    )
    return _scheduler


def stop_scheduler() -> None:
    """Para o scheduler. Chamado no shutdown do FastAPI."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Encerrado.")
