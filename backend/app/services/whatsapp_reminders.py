from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.appointment import Consulta
from backend.app.models.patient import Paciente
from backend.app.models.reminder import Lembrete
from backend.app.models.user import Usuario
from backend.app.models.whatsapp_interaction import InteracaoWhatsApp
from backend.app.services.whatsapp import (
    is_whatsapp_configured,
    normalize_whatsapp_phone,
    send_whatsapp_message,
)
from backend.app.services.whatsapp_content import (
    TemplateContext,
    get_template_content,
    render_template,
)
from backend.app.services.whatsapp_templates import (
    lembrete_paciente_whatsapp,
    patient_template_parameters,
)

logger = logging.getLogger(__name__)


async def _send_confirmation_reminder(
    db: Session,
    *,
    medico: Usuario,
    consulta: Consulta,
    paciente: Paciente,
    horas_antes: int,
    timezone: ZoneInfo,
) -> bool:
    settings = get_settings()
    telefone = normalize_whatsapp_phone(paciente.telefone)
    if not telefone:
        logger.warning("Paciente %s sem telefone válido para WhatsApp", paciente.id)
        return False

    idempotency_key = f"whatsapp_confirmacao:{consulta.id}:{horas_antes}"
    reminder = db.scalar(
        select(Lembrete).where(Lembrete.chave_idempotencia == idempotency_key)
    )
    if reminder and reminder.status == "enviado":
        return False

    clinic_name = medico.nome_clinica or "Agenda Médica"
    doctor_name = medico.nome or "Médico(a)"
    content = get_template_content(db, medico_id=medico.id, tipo="lembrete")
    body = render_template(
        content,
        TemplateContext(
            paciente=paciente.nome_completo,
            medico=doctor_name,
            inicio=consulta.inicio,
            clinica=clinic_name,
            telefone=medico.telefone or "",
            timezone=timezone,
        ),
    )
    approved_template = lembrete_paciente_whatsapp(
        paciente_nome=paciente.nome_completo,
        inicio=consulta.inicio,
        clinic_name=clinic_name,
        doctor_name=doctor_name,
        msg_personalizada=None,
        tz=timezone,
    )

    reminder_payload = {
        "telefone": telefone,
        "horas_antes": horas_antes,
        "template": settings.whatsapp_patient_template_name,
        "mensagem": body,
    }
    if reminder is None:
        reminder = Lembrete(
            id=uuid.uuid4(),
            consulta_id=consulta.id,
            canal="whatsapp_confirmacao",
            agendado_para=datetime.now(timezone),
            status="pendente",
            chave_idempotencia=idempotency_key,
            payload=reminder_payload,
        )
    else:
        reminder.status = "pendente"
        reminder.agendado_para = datetime.now(timezone)
        reminder.payload = reminder_payload
    db.add(reminder)
    db.flush()

    try:
        result = await send_whatsapp_message(
            to=telefone,
            body=body,
            template_name=settings.whatsapp_patient_template_name,
            language_code=settings.whatsapp_template_language,
            template_parameters=patient_template_parameters(
                approved_template,
                rendered_body=body,
                parameter_mode=settings.whatsapp_patient_template_parameter_mode,
            ),
            quick_reply_payloads=[
                f"confirmar:{consulta.id}",
                f"cancelar:{consulta.id}",
            ],
        )
        now = datetime.now(timezone)
        reminder.status = "enviado"
        reminder.enviado_em = now
        reminder.payload = {
            **(reminder.payload or {}),
            "message_id": result.message_id,
        }
        db.add(
            InteracaoWhatsApp(
                medico_id=medico.id,
                consulta_id=consulta.id,
                lembrete_id=reminder.id,
                event_id=result.message_id or f"out:{reminder.id}",
                telefone=telefone,
                direcao="saida",
                tipo="lembrete",
                status_processamento="enviado",
                payload=result.raw,
                processado_em=now,
            )
        )
        db.commit()
        return True
    except Exception as exc:
        reminder.status = "erro"
        reminder.payload = {**(reminder.payload or {}), "erro": str(exc)}
        db.add(reminder)
        db.commit()
        logger.exception("Falha no lembrete WhatsApp da consulta %s", consulta.id)
        return False


async def process_automatic_whatsapp_reminders(
    db: Session,
    *,
    now: datetime | None = None,
    window_minutes: int = 10,
) -> dict[str, int]:
    settings = get_settings()
    timezone = ZoneInfo(settings.app_timezone)
    current_time = (now or datetime.now(timezone)).astimezone(timezone)
    stats = {"enviados": 0, "erros": 0, "ignorados": 0}

    if not is_whatsapp_configured() or not settings.whatsapp_patient_template_name:
        logger.warning("WhatsApp ou template de paciente não configurado; lembretes não processados")
        return stats

    doctors = list(
        db.scalars(
            select(Usuario).where(
                and_(
                    Usuario.ativo.is_(True),
                    Usuario.lembrete_ativo.is_(True),
                )
            )
        ).all()
    )

    for doctor in doctors:
        configured_hours = sorted(set(doctor.lembrete_horas or [24, 2]), reverse=True)
        for hours_before in configured_hours:
            if hours_before <= 0:
                continue

            window_start = current_time + timedelta(hours=hours_before)
            window_end = window_start + timedelta(minutes=window_minutes)
            appointments = list(
                db.scalars(
                    select(Consulta)
                    .where(
                        and_(
                            Consulta.usuario_id == doctor.id,
                            Consulta.inicio >= window_start,
                            Consulta.inicio < window_end,
                            Consulta.status.in_(["agendada", "confirmada"]),
                        )
                    )
                    .order_by(Consulta.inicio.asc())
                ).all()
            )

            for appointment in appointments:
                patient = db.get(Paciente, appointment.paciente_id)
                if not patient:
                    stats["ignorados"] += 1
                    continue
                try:
                    sent = await _send_confirmation_reminder(
                        db,
                        medico=doctor,
                        consulta=appointment,
                        paciente=patient,
                        horas_antes=hours_before,
                        timezone=timezone,
                    )
                    stats["enviados" if sent else "ignorados"] += 1
                except Exception:
                    db.rollback()
                    stats["erros"] += 1
                    logger.exception("Erro ao processar consulta %s", appointment.id)

    return stats
