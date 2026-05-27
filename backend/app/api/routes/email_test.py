"""Rota de teste de e-mail — dispara lembretes reais para o médico e paciente."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.appointment import Consulta
from backend.app.models.patient import Paciente
from backend.app.utils.deps import get_current_user

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/test")
async def test_email(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> dict:
    """
    Envia e-mails de teste imediatamente:
    - 1 e-mail para o médico logado (resumo do dia)
    - 1 e-mail para o paciente da próxima consulta (se tiver e-mail cadastrado)

    Usa os templates reais de lembrete.
    """
    from backend.app.services.email import send_email
    from backend.app.services.email_templates import lembrete_medico_html, lembrete_paciente_html

    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone)
    now = datetime.now(tz)

    clinic_name = user.nome_clinica or "Agenda Médica"
    doctor_name = user.nome

    resultados = {}

    # ── 1. E-mail para o MÉDICO ───────────────────────────────────────────────
    email_medico = user.email_contato or user.email
    if not email_medico:
        resultados["medico"] = {"ok": False, "detalhe": "Médico sem e-mail configurado"}
    else:
        # Busca consultas de amanhã (ou hoje se não houver amanhã)
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

        # Se não tiver consultas amanhã, usa as próximas disponíveis
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

        if not consultas:
            # Cria dados fictícios para o teste
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
            # Enriquece com nome do paciente
            for c in consultas:
                p = db.get(Paciente, c.paciente_id)
                c._paciente_nome = p.nome_completo if p else "—"
                c._paciente_tel = p.telefone if p else ""
            consultas_exibir = consultas
            paciente_foco_nome = consultas[0]._paciente_nome
            inicio_foco = consultas[0].inicio

        subject, html = lembrete_medico_html(
            doctor_name=doctor_name,
            clinic_name=clinic_name,
            data_consultas=inicio_foco,
            consultas_do_dia=consultas_exibir,
            paciente_foco_nome=paciente_foco_nome,
            inicio_foco=inicio_foco,
            total_dia=len(consultas_exibir),
            msg_personalizada=user.lembrete_msg_medico,
        )

        try:
            ok = await send_email(to=email_medico, subject=f"[TESTE] {subject}", html=html)
            resultados["medico"] = {
                "ok": ok,
                "email": email_medico,
                "detalhe": "Enviado com sucesso" if ok else "SMTP não configurado",
            }
        except Exception as exc:
            resultados["medico"] = {"ok": False, "email": email_medico, "detalhe": str(exc)}

    # ── 2. E-mail para o PACIENTE ─────────────────────────────────────────────
    # Busca o próximo paciente com e-mail cadastrado
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
        if not paciente or not paciente.email:
            resultados["paciente"] = {
                "ok": False,
                "detalhe": f"Paciente '{paciente.nome_completo if paciente else '?'}' sem e-mail cadastrado. Edite o paciente e adicione um e-mail.",
            }
        else:
            # Histórico de consultas concluídas
            historico = list(db.scalars(
                select(Consulta).where(
                    and_(
                        Consulta.paciente_id == paciente.id,
                        Consulta.status == "concluida",
                    )
                ).order_by(Consulta.inicio.desc()).limit(10)
            ).all())

            subject, html = lembrete_paciente_html(
                paciente_nome=paciente.nome_completo,
                inicio=proxima.inicio,
                fim=proxima.fim,
                dias_antes=1,
                clinic_name=clinic_name,
                doctor_name=doctor_name,
                consultas_historico=historico,
                observacoes_consulta=proxima.observacoes,
                msg_personalizada=user.lembrete_msg_paciente,
            )

            try:
                ok = await send_email(
                    to=paciente.email,
                    subject=f"[TESTE] {subject}",
                    html=html,
                )
                resultados["paciente"] = {
                    "ok": ok,
                    "email": paciente.email,
                    "paciente": paciente.nome_completo,
                    "detalhe": "Enviado com sucesso" if ok else "SMTP não configurado",
                }
            except Exception as exc:
                resultados["paciente"] = {
                    "ok": False,
                    "email": paciente.email,
                    "paciente": paciente.nome_completo,
                    "detalhe": str(exc),
                }

    return {"ok": True, "resultados": resultados}
