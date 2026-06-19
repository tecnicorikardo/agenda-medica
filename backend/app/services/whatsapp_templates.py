"""Templates de lembretes para WhatsApp."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo


DEFAULT_PATIENT_MESSAGE = (
    "Olá, {primeiro_nome}!\n\n"
    "Lembramos que você tem uma consulta marcada para {data} às {hora}.\n\n"
    "Clínica: {clinica}\n"
    "Médico(a): {medico}\n\n"
    "Confirme sua presença ou entre em contato com antecedência caso precise remarcar."
)

DEFAULT_DOCTOR_MESSAGE = (
    "Olá, {medico}!\n\n"
    "Sua agenda de {data} tem {total_dia} consulta(s).\n\n"
    "{consultas}\n\n"
    "Primeira consulta: {paciente} às {hora}."
)


@dataclass(frozen=True)
class WhatsAppReminder:
    body: str
    template_parameters: list[str]


def patient_template_parameters(
    reminder: WhatsAppReminder,
    *,
    rendered_body: str,
    parameter_mode: str,
) -> list[str]:
    normalized_mode = parameter_mode.strip().lower()
    if normalized_mode == "message":
        return [rendered_body]
    if normalized_mode in {"standard", "standart"}:
        return reminder.template_parameters
    raise ValueError(
        "WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE deve ser 'standard' ou 'message'."
    )


def patient_quick_reply_payloads(
    appointment_id: UUID,
    *,
    quick_reply_count: int,
) -> list[str]:
    payloads = [
        f"confirmar:{appointment_id}",
        f"cancelar:{appointment_id}",
    ]
    if quick_reply_count < 0 or quick_reply_count > len(payloads):
        raise ValueError("O template de paciente suporta entre 0 e 2 quick replies.")
    return payloads[:quick_reply_count]


def _first_name(name: str | None) -> str:
    parts = (name or "").strip().split()
    return parts[0] if parts else "Paciente"


def _format_date_time(value: datetime, tz: ZoneInfo) -> tuple[str, str]:
    local_value = value.astimezone(tz)
    return local_value.strftime("%d/%m/%Y"), local_value.strftime("%H:%M")


def _render(template: str, values: dict[str, str]) -> str:
    message = template
    for key, value in values.items():
        message = message.replace("{" + key + "}", value)
    return message.strip()


def lembrete_paciente_whatsapp(
    *,
    paciente_nome: str,
    inicio: datetime,
    clinic_name: str,
    doctor_name: str | None,
    msg_personalizada: str | None,
    tz: ZoneInfo,
) -> WhatsAppReminder:
    data, hora = _format_date_time(inicio, tz)
    medico = doctor_name or "médico(a)"
    primeiro_nome = _first_name(paciente_nome)
    values = {
        "primeiro_nome": primeiro_nome,
        "nome": paciente_nome,
        "data": data,
        "hora": hora,
        "clinica": clinic_name,
        "medico": medico,
    }
    body = _render(msg_personalizada or DEFAULT_PATIENT_MESSAGE, values)
    return WhatsAppReminder(
        body=body,
        template_parameters=[primeiro_nome, data, hora, clinic_name, medico],
    )


def lembrete_medico_whatsapp(
    *,
    doctor_name: str | None,
    clinic_name: str,
    data_consultas: datetime,
    consultas_do_dia: list,
    paciente_foco_nome: str,
    inicio_foco: datetime,
    msg_personalizada: str | None,
    tz: ZoneInfo,
) -> WhatsAppReminder:
    data, hora = _format_date_time(inicio_foco, tz)
    medico = doctor_name or "Doutor(a)"
    resumo_linhas: list[str] = []

    for consulta in consultas_do_dia:
        _, hora_consulta = _format_date_time(consulta.inicio, tz)
        paciente_nome = getattr(consulta, "_paciente_nome", None) or "Paciente"
        paciente_tel = getattr(consulta, "_paciente_tel", None) or ""
        detalhe_tel = f" - {paciente_tel}" if paciente_tel else ""
        resumo_linhas.append(f"{hora_consulta} - {paciente_nome}{detalhe_tel}")

    resumo = "\n".join(resumo_linhas)
    values = {
        "medico": medico,
        "paciente": paciente_foco_nome,
        "data": data,
        "hora": hora,
        "clinica": clinic_name,
        "total_dia": str(len(consultas_do_dia)),
        "consultas": resumo,
    }
    body = _render(msg_personalizada or DEFAULT_DOCTOR_MESSAGE, values)
    return WhatsAppReminder(
        body=body,
        template_parameters=[medico, data, str(len(consultas_do_dia)), resumo, clinic_name],
    )
