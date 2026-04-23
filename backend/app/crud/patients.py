from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.patient import Paciente
from backend.app.schemas.patient import PacienteCreate, PacienteUpdate


def list_patients(db: Session, *, usuario_id, search: str | None, limit: int = 50) -> list[Paciente]:
    stmt = (
        select(Paciente)
        .where(Paciente.usuario_id == usuario_id)
        .order_by(Paciente.nome_completo.asc())
    )
    if search and search.strip():
        q = f"%{search.strip()}%"
        q_starts = f"{search.strip()}%"
        stmt = stmt.where(or_(Paciente.nome_completo.ilike(q), Paciente.telefone.ilike(q)))
        # Ordena: quem começa com o termo vem primeiro
        from sqlalchemy import case
        stmt = stmt.order_by(
            case((Paciente.nome_completo.ilike(q_starts), 0), else_=1),
            Paciente.nome_completo.asc(),
        )
        stmt = stmt.limit(10)
    else:
        stmt = stmt.limit(limit)
    return list(db.scalars(stmt).all())


def get_patient(db: Session, patient_id) -> Paciente | None:
    return db.get(Paciente, patient_id)


def create_patient(db: Session, *, usuario_id, data: PacienteCreate) -> Paciente:
    patient = Paciente(usuario_id=usuario_id, **data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient: Paciente, data: PacienteUpdate) -> Paciente:
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(patient, k, v)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: Paciente) -> None:
    db.delete(patient)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Não é possível excluir: paciente possui consultas vinculadas.") from exc
