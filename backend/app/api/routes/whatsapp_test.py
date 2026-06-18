"""Rota de teste de WhatsApp para médico e paciente."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.appointment import Consulta
from backend.app.models.patient import Paciente
from backend.app.services.whatsapp import (
    is_whatsapp_configured,
    normalize_whatsapp_phone,
    send_whatsapp_message,
)
from backend.app.services.whatsapp_templates import (
    lembrete_medico_whatsapp,
    lembrete_paciente_whatsapp,
    patient_template_parameters,
)
from backend.app.utils.deps import get_current_user

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


def _canal_descricao(template_name: str) -> str:
    return f"template '{template_name}'" if template_name else "texto livre"


@router.post("/test")
async def test_whatsapp(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> dict:
    """Envia mensagens reais de teste via WhatsApp Cloud API."""
    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone)
    now = datetime.now(tz)
    clinic_name = user.nome_clinica or "Agenda Médica"

    resultados = {}
    configurado = is_whatsapp_configured()

    if not configurado:
        detalhe = "WhatsApp não configurado. Defina WHATSAPP_ACCESS_TOKEN e WHATSAPP_PHONE_NUMBER_ID."
        return {
            "ok": True,
            "configured": False,
            "resultados": {
                "medico": {"ok": False, "telefone": user.telefone, "detalhe": detalhe},
                "paciente": {"ok": False, "detalhe": detalhe},
            },
        }

    amanha_inicio = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=tz) + timedelta(days=1)
    amanha_fim = amanha_inicio + timedelta(days=1)
    consultas = list(db.scalars(
        select(Consulta).where(
            and_(
                Consulta.usuario_id == user.id,
                Consulta.inicio >= amanha_inicio,
                Consulta.inicio < amanha_fim,
                Consulta.status.in_(["agendada", "confirmada"]),
            )
        ).order_by(Consulta.inicio.asc())
    ).all())

    if not consultas:
        consultas = list(db.scalars(
            select(Consulta).where(
                and_(
                    Consulta.usuario_id == user.id,
                    Consulta.inicio >= now,
                    Consulta.status.in_(["agendada", "confirmada"]),
                )
            ).order_by(Consulta.inicio.asc()).limit(5)
        ).all())

    telefone_medico = normalize_whatsapp_phone(user.telefone)
    if not telefone_medico:
        resultados["medico"] = {
            "ok": False,
            "telefone": user.telefone,
            "detalhe": "Médico sem telefone válido no perfil.",
        }
    else:
        if not consultas:
            inicio_fake = now + timedelta(days=1, hours=9)
            fim_fake = inicio_fake + timedelta(minutes=30)

            class FakeConsulta:
                inicio = inicio_fake
                fim = fim_fake
                status = "agendada"
                observacoes = None
                _paciente_nome = "Paciente Teste"
                _paciente_tel = "(11) 99999-9999"

            consultas_exibir = [FakeConsulta()]
            paciente_foco_nome = "Paciente Teste"
            inicio_foco = inicio_fake
        else:
            for consulta in consultas:
                paciente = db.get(Paciente, consulta.paciente_id)
                consulta._paciente_nome = paciente.nome_completo if paciente else "—"
                consulta._paciente_tel = paciente.telefone if paciente else ""
            consultas_exibir = consultas
            paciente_foco_nome = consultas[0]._paciente_nome
            inicio_foco = consultas[0].inicio

        reminder = lembrete_medico_whatsapp(
            doctor_name=user.nome,
            clinic_name=clinic_name,
            data_consultas=inicio_foco,
            consultas_do_dia=consultas_exibir,
            paciente_foco_nome=paciente_foco_nome,
            inicio_foco=inicio_foco,
            msg_personalizada=user.lembrete_msg_medico,
            tz=tz,
        )

        try:
            await send_whatsapp_message(
                to=telefone_medico,
                body=f"[TESTE]\n{reminder.body}",
                template_name=settings.whatsapp_doctor_template_name,
                language_code=settings.whatsapp_template_language,
                template_parameters=reminder.template_parameters,
            )
            resultados["medico"] = {
                "ok": True,
                "telefone": telefone_medico,
                "detalhe": f"Enviado com sucesso via {_canal_descricao(settings.whatsapp_doctor_template_name)}.",
            }
        except Exception as exc:
            resultados["medico"] = {"ok": False, "telefone": telefone_medico, "detalhe": str(exc)}

    proxima = db.scalar(
        select(Consulta).where(
            and_(
                Consulta.usuario_id == user.id,
                Consulta.inicio >= now,
                Consulta.status.in_(["agendada", "confirmada"]),
            )
        ).order_by(Consulta.inicio.asc())
    )

    if not proxima:
        resultados["paciente"] = {
            "ok": False,
            "detalhe": "Nenhuma consulta futura encontrada. Agende uma consulta primeiro.",
        }
    else:
        paciente = db.get(Paciente, proxima.paciente_id)
        telefone_paciente = normalize_whatsapp_phone(paciente.telefone if paciente else None)
        if not paciente or not telefone_paciente:
            resultados["paciente"] = {
                "ok": False,
                "telefone": paciente.telefone if paciente else None,
                "detalhe": f"Paciente '{paciente.nome_completo if paciente else '?'}' sem telefone válido.",
            }
        else:
            reminder = lembrete_paciente_whatsapp(
                paciente_nome=paciente.nome_completo,
                inicio=proxima.inicio,
                clinic_name=clinic_name,
                doctor_name=user.nome,
                msg_personalizada=user.lembrete_msg_paciente,
                tz=tz,
            )
            try:
                await send_whatsapp_message(
                    to=telefone_paciente,
                    body=f"[TESTE]\n{reminder.body}",
                    template_name=settings.whatsapp_patient_template_name,
                    language_code=settings.whatsapp_template_language,
                    template_parameters=patient_template_parameters(
                        reminder,
                        rendered_body=reminder.body,
                        parameter_mode=settings.whatsapp_patient_template_parameter_mode,
                    ),
                    quick_reply_payloads=[
                        f"confirmar:{proxima.id}",
                        f"cancelar:{proxima.id}",
                    ],
                )
                resultados["paciente"] = {
                    "ok": True,
                    "telefone": telefone_paciente,
                    "paciente": paciente.nome_completo,
                    "detalhe": f"Enviado com sucesso via {_canal_descricao(settings.whatsapp_patient_template_name)}.",
                }
            except Exception as exc:
                resultados["paciente"] = {
                    "ok": False,
                    "telefone": telefone_paciente,
                    "paciente": paciente.nome_completo,
                    "detalhe": str(exc),
                }

    return {"ok": True, "configured": True, "resultados": resultados}
