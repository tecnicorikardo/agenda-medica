from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import Usuario


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def get_by_id(db: Session, user_id) -> Usuario | None:
    return db.get(Usuario, user_id)

