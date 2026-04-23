from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from backend.app.models.appointment import Consulta
from backend.app.schemas.appointment import ConsultaCreate, ConsultaUpdate
from backend.app.core.config import get_settings


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    tz = ZoneInfo(get_settings().app_timezone)
    start = datetime.combine(day, time.min, tzinfo=tz)
    end = start + timedelta(days=1)
    return start, end


def list_by_day(db: Session, *, usuario_id, day: date) -> list[Consulta]:
    start, end = _day_bounds(day)
    stmt = (
        select(Consulta)
        .where(and_(Consulta.usuario_id == usuario_id, Consulta.inicio >= start, Consulta.inicio < end))
        .order_by(Consulta.inicio.asc())
    )
    return list(db.scalars(stmt).all())


def list_by_range(db: Session, *, usuario_id, start: datetime, end: datetime) -> list[Consulta]:
    stmt = (
        select(Consulta)
        .where(and_(Consulta.usuario_id == usuario_id, Consulta.inicio >= start, Consulta.inicio < end))
        .order_by(Consulta.inicio.asc())
    )
    return list(db.scalars(stmt).all())


def list_upcoming(db: Session, *, usuario_id, now: datetime, limit: int = 20) -> list[Consulta]:
    stmt = (
        select(Consulta)
        .where(and_(Consulta.usuario_id == usuario_id, Consulta.fim > now, Consulta.status != "cancelada"))
        .order_by(Consulta.inicio.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get(db: Session, consulta_id) -> Consulta | None:
    return db.get(Consulta, consulta_id)


def has_conflict(db: Session, *, usuario_id, inicio: datetime, fim: datetime, ignore_id=None) -> bool:
    conditions = [
        Consulta.usuario_id == usuario_id,
        Consulta.status != "cancelada",
        Consulta.inicio < fim,
        Consulta.fim > inicio,
    ]
    if ignore_id is not None:
        conditions.append(Consulta.id != ignore_id)
    stmt = select(func.count()).select_from(Consulta).where(and_(*conditions))
    return (db.scalar(stmt) or 0) > 0


def create(db: Session, *, usuario_id, data: ConsultaCreate) -> Consulta:
    if data.fim <= data.inicio:
        raise ValueError("Horário final deve ser maior que o inicial")
    if has_conflict(db, usuario_id=usuario_id, inicio=data.inicio, fim=data.fim):
        raise ValueError("Conflito de horário: já existe consulta nesse intervalo")
    consulta = Consulta(usuario_id=usuario_id, **data.model_dump())
    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta


def update(db: Session, *, usuario_id, consulta: Consulta, data: ConsultaUpdate) -> Consulta:
    updates = data.model_dump(exclude_unset=True)

    novo_inicio = updates.get("inicio", consulta.inicio)
    novo_fim = updates.get("fim", consulta.fim)
    if novo_fim <= novo_inicio:
        raise ValueError("Horário final deve ser maior que o inicial")

    if ("inicio" in updates) or ("fim" in updates):
        if has_conflict(db, usuario_id=usuario_id, inicio=novo_inicio, fim=novo_fim, ignore_id=consulta.id):
            raise ValueError("Conflito de horário: já existe consulta nesse intervalo")

    for k, v in updates.items():
        setattr(consulta, k, v)

    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta


def cancel(db: Session, consulta: Consulta) -> Consulta:
    consulta.status = "cancelada"
    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta


def mark_status(db: Session, consulta: Consulta, status: str) -> Consulta:
    consulta.status = status
    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta
