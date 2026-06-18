from __future__ import annotations

import hashlib
import hmac
import logging
import unicodedata
from datetime import datetime, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import SessionLocal
from backend.app.models.appointment import Consulta
from backend.app.models.patient import Paciente
from backend.app.models.reminder import Lembrete
from backend.app.models.user import Usuario
from backend.app.models.whatsapp_interaction import InteracaoWhatsApp
from backend.app.services.whatsapp import normalize_whatsapp_phone, send_whatsapp_text
from backend.app.services.whatsapp_content import (
    TemplateContext,
    get_template_content,
    render_template,
)

logger = logging.getLogger(__name__)


def verify_whatsapp_signature(raw_body: bytes, signature: str | None, app_secret: str) -> bool:
    if not app_secret:
        return True
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


def iter_webhook_events(payload: dict) -> list[dict]:
    events: list[dict] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value") or {}
            for message in value.get("messages", []):
                events.append({
                    "kind": "message",
                    "event_id": message.get("id"),
                    "phone": message.get("from"),
                    "message": message,
                    "metadata": value.get("metadata") or {},
                })
            for status in value.get("statuses", []):
                event_id = ":".join(
                    [
                        "status",
                        str(status.get("id") or ""),
                        str(status.get("status") or ""),
                        str(status.get("timestamp") or ""),
                    ]
                )
                events.append({
                    "kind": "status",
                    "event_id": event_id,
                    "phone": status.get("recipient_id"),
                    "status": status,
                    "metadata": value.get("metadata") or {},
                })
    return [event for event in events if event.get("event_id")]


def extract_button_action(message: dict) -> tuple[str | None, UUID | None, str | None]:
    payload = None
    label = None
    message_type = message.get("type")

    if message_type == "button":
        button = message.get("button") or {}
        payload = button.get("payload")
        label = button.get("text")
    elif message_type == "interactive":
        reply = (message.get("interactive") or {}).get("button_reply") or {}
        payload = reply.get("id")
        label = reply.get("title")

    action, appointment_id = _parse_action_payload(payload)
    if not action:
        action, _ = _parse_action_payload(label)
    context_message_id = (message.get("context") or {}).get("id")
    return action, appointment_id, context_message_id


def _parse_action_payload(value: str | None) -> tuple[str | None, UUID | None]:
    if not value:
        return None, None

    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", value.lower().strip())
        if not unicodedata.combining(char)
    )
    appointment_id = None
    if ":" in normalized:
        action_text, raw_id = normalized.split(":", 1)
        try:
            appointment_id = UUID(raw_id)
        except ValueError:
            appointment_id = None
    else:
        action_text = normalized

    if action_text in {"confirmar", "confirmar consulta", "confirmado", "sim"}:
        return "confirmar", appointment_id
    if action_text in {"cancelar", "cancelar consulta", "cancelado", "nao"}:
        return "cancelar", appointment_id
    return None, appointment_id


def _find_reminder(
    db: Session,
    *,
    appointment_id: UUID | None,
    context_message_id: str | None,
) -> Lembrete | None:
    conditions = [
        Lembrete.canal == "whatsapp_confirmacao",
        Lembrete.status == "enviado",
    ]
    if appointment_id:
        conditions.append(Lembrete.consulta_id == appointment_id)
    if context_message_id:
        conditions.append(Lembrete.payload["message_id"].as_string() == context_message_id)
    if not appointment_id and not context_message_id:
        return None
    return db.scalar(
        select(Lembrete)
        .where(and_(*conditions))
        .order_by(Lembrete.enviado_em.desc())
        .limit(1)
    )


def _event_already_processed(db: Session, event_id: str) -> bool:
    return db.scalar(
        select(InteracaoWhatsApp.id).where(InteracaoWhatsApp.event_id == event_id)
    ) is not None


def _record_status_event(db: Session, event: dict) -> None:
    status = event["status"]
    message_id = status.get("id")
    reminder = None
    if message_id:
        reminder = db.scalar(
            select(Lembrete)
            .where(Lembrete.payload["message_id"].as_string() == message_id)
            .order_by(Lembrete.enviado_em.desc())
            .limit(1)
        )
    appointment = db.get(Consulta, reminder.consulta_id) if reminder else None
    if reminder:
        reminder.payload = {
            **(reminder.payload or {}),
            "ultimo_status_meta": status.get("status"),
            "status_meta_em": status.get("timestamp"),
        }
        db.add(reminder)
    db.add(
        InteracaoWhatsApp(
            medico_id=appointment.usuario_id if appointment else None,
            consulta_id=appointment.id if appointment else None,
            lembrete_id=reminder.id if reminder else None,
            event_id=event["event_id"],
            telefone=normalize_whatsapp_phone(event.get("phone")),
            direcao="status",
            tipo=str(status.get("status") or "desconhecido"),
            status_processamento="registrado",
            payload=status,
            processado_em=datetime.now(timezone.utc),
        )
    )
    db.commit()


async def _send_status_response(
    db: Session,
    *,
    interaction: InteracaoWhatsApp,
    doctor: Usuario,
    patient: Paciente,
    appointment: Consulta,
    action: str,
    phone: str,
) -> None:
    settings = get_settings()
    timezone_info = ZoneInfo(settings.app_timezone)
    template_type = "confirmacao" if action == "confirmar" else "cancelamento"
    content = get_template_content(db, medico_id=doctor.id, tipo=template_type)
    body = render_template(
        content,
        TemplateContext(
            paciente=patient.nome_completo,
            medico=doctor.nome or "Médico(a)",
            inicio=appointment.inicio,
            clinica=doctor.nome_clinica or "Agenda Médica",
            telefone=doctor.telefone or "",
            timezone=timezone_info,
        ),
    )

    try:
        result = await send_whatsapp_text(to=phone, body=body)
        db.add(
            InteracaoWhatsApp(
                medico_id=doctor.id,
                consulta_id=appointment.id,
                lembrete_id=interaction.lembrete_id,
                event_id=result.message_id or f"response:{interaction.id}",
                telefone=phone,
                direcao="saida",
                tipo=template_type,
                acao=action,
                status_processamento="enviado",
                payload=result.raw,
                processado_em=datetime.now(timezone.utc),
            )
        )
        db.commit()
    except Exception as exc:
        interaction.erro = f"Status atualizado, mas a resposta não foi enviada: {exc}"
        db.add(interaction)
        db.commit()
        logger.exception("Falha ao responder interação WhatsApp %s", interaction.event_id)


async def _process_message_event(db: Session, event: dict) -> None:
    message = event["message"]
    action, appointment_id, context_message_id = extract_button_action(message)
    phone = normalize_whatsapp_phone(event.get("phone"))
    reminder = _find_reminder(
        db,
        appointment_id=appointment_id,
        context_message_id=context_message_id,
    )
    appointment = db.get(Consulta, reminder.consulta_id) if reminder else None
    doctor = db.get(Usuario, appointment.usuario_id) if appointment and appointment.usuario_id else None
    patient = db.get(Paciente, appointment.paciente_id) if appointment else None

    interaction = InteracaoWhatsApp(
        medico_id=doctor.id if doctor else None,
        consulta_id=appointment.id if appointment else appointment_id,
        lembrete_id=reminder.id if reminder else None,
        event_id=event["event_id"],
        telefone=phone,
        direcao="entrada",
        tipo=message.get("type") or "mensagem",
        acao=action,
        status_processamento="recebido",
        payload=message,
    )
    db.add(interaction)

    if not action:
        interaction.status_processamento = "ignorado"
        interaction.erro = "Mensagem recebida sem ação de confirmação ou cancelamento."
        interaction.processado_em = datetime.now(timezone.utc)
        db.commit()
        return
    if not reminder or not appointment or not doctor or not patient:
        interaction.status_processamento = "ignorado"
        interaction.erro = "Não foi possível relacionar a resposta a uma consulta."
        interaction.processado_em = datetime.now(timezone.utc)
        db.commit()
        return
    if phone != normalize_whatsapp_phone(patient.telefone):
        interaction.status_processamento = "rejeitado"
        interaction.erro = "O telefone da resposta não corresponde ao paciente da consulta."
        interaction.processado_em = datetime.now(timezone.utc)
        db.commit()
        return

    now = datetime.now(timezone.utc)
    if action == "confirmar" and appointment.status == "agendada":
        appointment.status = "confirmada"
        appointment.data_confirmacao = now
        appointment.data_cancelamento = None
    elif action == "cancelar" and appointment.status in {"agendada", "confirmada"}:
        appointment.status = "cancelada"
        appointment.data_cancelamento = now
    elif (
        action == "confirmar"
        and appointment.status == "confirmada"
        or action == "cancelar"
        and appointment.status == "cancelada"
    ):
        interaction.status_processamento = "duplicado"
        interaction.processado_em = now
        db.commit()
        return
    else:
        interaction.status_processamento = "ignorado"
        interaction.erro = f"A consulta está com status '{appointment.status}'."
        interaction.processado_em = now
        db.commit()
        return

    interaction.status_processamento = "processado"
    interaction.processado_em = now
    db.add(appointment)
    db.commit()
    await _send_status_response(
        db,
        interaction=interaction,
        doctor=doctor,
        patient=patient,
        appointment=appointment,
        action=action,
        phone=phone,
    )


async def process_whatsapp_webhook(payload: dict) -> None:
    for event in iter_webhook_events(payload):
        with SessionLocal() as db:
            try:
                if _event_already_processed(db, event["event_id"]):
                    continue
                if event["kind"] == "status":
                    _record_status_event(db, event)
                else:
                    await _process_message_event(db, event)
            except Exception:
                db.rollback()
                logger.exception("Erro ao processar evento WhatsApp %s", event["event_id"])
