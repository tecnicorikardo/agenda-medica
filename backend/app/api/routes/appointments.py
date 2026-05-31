from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.patients import get_patient
from backend.app.crud.appointments import (
    cancel,
    create,
    get,
    list_by_day,
    list_by_range,
    list_upcoming,
    mark_status,
    update,
)
from backend.app.db.session import get_db
from backend.app.schemas.appointment import ConsultaCreate, ConsultaUpdate, ConsultaWithPaciente
from backend.app.utils.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


async def _enviar_confirmacao_agendamento(
    *,
    email_dest: str,
    paciente_nome: str,
    inicio: datetime,
    fim: datetime,
    clinic_name: str,
    doctor_name: str | None,
    observacoes_consulta: str | None,
) -> None:
    from backend.app.services.email import send_email
    from backend.app.services.email_templates import confirmacao_agendamento_paciente_html

    subject, html = confirmacao_agendamento_paciente_html(
        paciente_nome=paciente_nome,
        inicio=inicio,
        fim=fim,
        clinic_name=clinic_name,
        doctor_name=doctor_name,
        observacoes_consulta=observacoes_consulta,
    )

    try:
        ok = await send_email(to=email_dest, subject=subject, html=html)
        if not ok:
            logger.warning("Confirmação de agendamento não enviada para %s: e-mail não configurado", email_dest)
    except Exception as exc:
        logger.exception("Erro ao enviar confirmação de agendamento para %s: %s", email_dest, exc)


def _as_with_paciente(consulta) -> dict:
    paciente = getattr(consulta, "paciente", None)
    return {
        "id": consulta.id,
        "paciente_id": consulta.paciente_id,
        "inicio": consulta.inicio,
        "fim": consulta.fim,
        "status": consulta.status,
        "observacoes": consulta.observacoes,
        "created_at": consulta.created_at,
        "updated_at": consulta.updated_at,
        "paciente_nome": paciente.nome_completo if paciente else "",
        "paciente_telefone": paciente.telefone if paciente else "",
        "paciente_email": paciente.email if paciente else None,
    }


@router.get("", response_model=list[ConsultaWithPaciente])
def list_(
    day: date,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[ConsultaWithPaciente]:
    consultas = list_by_day(db, usuario_id=user.id, day=day)
    return [_as_with_paciente(c) for c in consultas]


@router.get("/range", response_model=list[ConsultaWithPaciente])
def list_range(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[ConsultaWithPaciente]:
    from datetime import time
    from zoneinfo import ZoneInfo
    from backend.app.core.config import get_settings
    tz = ZoneInfo(get_settings().app_timezone)
    dt_start = datetime.combine(start, time.min, tzinfo=tz)
    dt_end = datetime.combine(end, time.min, tzinfo=tz) + __import__("datetime").timedelta(days=1)
    consultas = list_by_range(db, usuario_id=user.id, start=dt_start, end=dt_end)
    return [_as_with_paciente(c) for c in consultas]


@router.get("/upcoming", response_model=list[ConsultaWithPaciente])
def upcoming(
    limit: int = 20,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[ConsultaWithPaciente]:
    now = datetime.now(timezone.utc)
    consultas = list_upcoming(db, usuario_id=user.id, now=now, limit=min(max(limit, 1), 100))
    return [_as_with_paciente(c) for c in consultas]


@router.post("", response_model=ConsultaWithPaciente, status_code=status.HTTP_201_CREATED)
def create_(
    data: ConsultaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ConsultaWithPaciente:
    patient = get_patient(db, data.paciente_id)
    if not patient or patient.usuario_id != user.id:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    try:
        consulta = create(db, usuario_id=user.id, data=data)
        if patient.email:
            background_tasks.add_task(
                _enviar_confirmacao_agendamento,
                email_dest=patient.email,
                paciente_nome=patient.nome_completo,
                inicio=consulta.inicio,
                fim=consulta.fim,
                clinic_name=user.nome_clinica or "Agenda Médica",
                doctor_name=user.nome,
                observacoes_consulta=consulta.observacoes,
            )
        return _as_with_paciente(consulta)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{consulta_id}", response_model=ConsultaWithPaciente)
def update_(
    consulta_id,
    data: ConsultaUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ConsultaWithPaciente:
    consulta = get(db, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if consulta.usuario_id != user.id:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    try:
        consulta = update(db, usuario_id=user.id, consulta=consulta, data=data)
        return _as_with_paciente(consulta)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{consulta_id}/cancel", response_model=ConsultaWithPaciente)
def cancel_(
    consulta_id,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ConsultaWithPaciente:
    consulta = get(db, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if consulta.usuario_id != user.id:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    consulta = cancel(db, consulta)
    return _as_with_paciente(consulta)


@router.post("/{consulta_id}/status/{status_name}", response_model=ConsultaWithPaciente)
def set_status(
    consulta_id,
    status_name: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ConsultaWithPaciente:
    if status_name not in {"agendada", "confirmada", "concluida", "cancelada", "faltou"}:
        raise HTTPException(status_code=400, detail="Status inválido")
    consulta = get(db, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if consulta.usuario_id != user.id:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    consulta = mark_status(db, consulta, status_name)
    return _as_with_paciente(consulta)
