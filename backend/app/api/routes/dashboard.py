from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.appointment import Consulta
from backend.app.models.patient import Paciente
from backend.app.schemas.dashboard import DashboardOut, SlotLivre
from backend.app.utils.deps import get_current_user

router = APIRouter()


def _bounds_for_day(day: date) -> tuple[datetime, datetime]:
    tz = ZoneInfo(get_settings().app_timezone)
    start = datetime.combine(day, time.min, tzinfo=tz)
    return start, start + timedelta(days=1)


def _free_slots(day: date, consultas: list[Consulta]) -> list[SlotLivre]:
    # Regra simples (pode evoluir): 08:00-18:00, slots de 30 min
    tz = ZoneInfo(get_settings().app_timezone)
    start_day = datetime.combine(day, time(8, 0), tzinfo=tz)
    end_day = datetime.combine(day, time(18, 0), tzinfo=tz)

    busy = [(c.inicio, c.fim) for c in consultas if c.status != "cancelada"]
    busy.sort(key=lambda x: x[0])

    slots: list[SlotLivre] = []
    cursor = start_day
    slot_len = timedelta(minutes=30)

    def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
        return a_start < b_end and a_end > b_start

    while cursor + slot_len <= end_day:
        s = cursor
        e = cursor + slot_len
        if not any(overlaps(s, e, b0, b1) for (b0, b1) in busy):
            slots.append(SlotLivre(inicio=s, fim=e))
        cursor = cursor + slot_len
    return slots[:10]


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(
    dia: date | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> DashboardOut:
    tz = ZoneInfo(get_settings().app_timezone)
    day = dia or datetime.now(tz).date()
    start, end = _bounds_for_day(day)

    consultas_do_dia = db.scalar(
        select(func.count())
        .select_from(Consulta)
        .where(and_(Consulta.usuario_id == user.id, Consulta.inicio >= start, Consulta.inicio < end))
    ) or 0

    pacientes_cadastrados = db.scalar(
        select(func.count()).select_from(Paciente).where(Paciente.usuario_id == user.id)
    ) or 0

    consultas_canceladas = db.scalar(
        select(func.count())
        .select_from(Consulta)
        .where(
            and_(
                Consulta.usuario_id == user.id,
                Consulta.inicio >= start,
                Consulta.inicio < end,
                Consulta.status == "cancelada",
            )
        )
    ) or 0

    atendimentos_concluidos = db.scalar(
        select(func.count())
        .select_from(Consulta)
        .where(
            and_(
                Consulta.usuario_id == user.id,
                Consulta.inicio >= start,
                Consulta.inicio < end,
                Consulta.status == "concluida",
            )
        )
    ) or 0

    consultas = list(
        db.scalars(
            select(Consulta)
            .where(and_(Consulta.usuario_id == user.id, Consulta.inicio >= start, Consulta.inicio < end))
            .order_by(Consulta.inicio.asc())
        ).all()
    )

    now = datetime.now(tz)
    proxima = next((c for c in consultas if c.fim > now and c.status != "cancelada"), None)

    return DashboardOut(
        dia=day,
        consultas_do_dia=int(consultas_do_dia),
        proximo_paciente=None
        if not proxima
        else {
            "id": proxima.id,
            "paciente_id": proxima.paciente_id,
            "inicio": proxima.inicio,
            "fim": proxima.fim,
            "status": proxima.status,
            "observacoes": proxima.observacoes,
            "created_at": proxima.created_at,
            "updated_at": proxima.updated_at,
            "paciente_nome": proxima.paciente.nome_completo if proxima.paciente else "",
            "paciente_telefone": proxima.paciente.telefone if proxima.paciente else "",
        },
        horarios_livres=_free_slots(day, consultas),
        pacientes_cadastrados=int(pacientes_cadastrados),
        consultas_canceladas=int(consultas_canceladas),
        atendimentos_concluidos=int(atendimentos_concluidos),
    )
