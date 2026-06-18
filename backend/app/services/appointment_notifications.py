from __future__ import annotations

import logging
from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from backend.app.core.config import get_settings
from backend.app.db.session import SessionLocal
from backend.app.models.appointment import Consulta
from backend.app.models.patient import Paciente
from backend.app.services.push import send_push_to_subscriptions

logger = logging.getLogger(__name__)

AppointmentEvent = Literal["created", "updated", "rescheduled", "status_changed"]

STATUS_TITLES = {
    "agendada": "Consulta agendada",
    "confirmada": "Consulta confirmada",
    "concluida": "Consulta concluída",
    "cancelada": "Consulta cancelada",
    "faltou": "Paciente não compareceu",
}

FIELD_LABELS = {
    "inicio": "horário inicial",
    "fim": "horário final",
    "observacoes": "observações",
    "paciente_id": "paciente",
}


def classify_appointment_event(changed_fields: set[str]) -> AppointmentEvent | None:
    if not changed_fields:
        return None
    if "status" in changed_fields:
        return "status_changed"
    if changed_fields.intersection({"inicio", "fim"}):
        return "rescheduled"
    return "updated"


def build_appointment_push_message(
    *,
    event: AppointmentEvent,
    patient_name: str,
    starts_at: datetime,
    appointment_status: str,
    timezone_name: str,
    changed_fields: tuple[str, ...] = (),
    source: str = "app",
) -> tuple[str, str]:
    timezone_info = ZoneInfo(timezone_name)
    if starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone_info)
    local_start = starts_at.astimezone(timezone_info)
    schedule = f"{local_start:%d/%m/%Y} às {local_start:%H:%M}"

    if event == "created":
        return "Nova consulta agendada", f"{patient_name} • {schedule}."

    if event == "rescheduled":
        return "Consulta reagendada", f"{patient_name} • novo horário: {schedule}."

    if event == "status_changed":
        title = STATUS_TITLES.get(appointment_status, "Status da consulta alterado")
        if source == "whatsapp" and appointment_status in {"confirmada", "cancelada"}:
            action = "confirmou" if appointment_status == "confirmada" else "cancelou"
            return title, f"{patient_name} {action} a consulta de {schedule} pelo WhatsApp."
        return title, f"{patient_name} • {schedule}."

    labels = [FIELD_LABELS[field] for field in changed_fields if field in FIELD_LABELS]
    detail = f" Alterado: {', '.join(labels)}." if labels else ""
    return "Consulta atualizada", f"{patient_name} • {schedule}.{detail}"


def send_appointment_push_notification(
    *,
    appointment_id: UUID,
    event: AppointmentEvent,
    changed_fields: tuple[str, ...] = (),
    source: str = "app",
) -> int:
    try:
        with SessionLocal() as db:
            appointment = db.get(Consulta, appointment_id)
            if not appointment or not appointment.usuario_id:
                return 0

            patient = db.get(Paciente, appointment.paciente_id)
            patient_name = patient.nome_completo if patient else "Paciente"
            title, body = build_appointment_push_message(
                event=event,
                patient_name=patient_name,
                starts_at=appointment.inicio,
                appointment_status=appointment.status,
                timezone_name=get_settings().app_timezone,
                changed_fields=changed_fields,
                source=source,
            )
            return send_push_to_subscriptions(
                db,
                usuario_id=appointment.usuario_id,
                title=title,
                body=body,
                url="/#/agenda",
                tag=f"consulta-{appointment.id}-{event}-{uuid4().hex}",
            )
    except Exception:
        logger.exception(
            "Falha ao enviar push do evento %s para a consulta %s",
            event,
            appointment_id,
        )
        return 0
