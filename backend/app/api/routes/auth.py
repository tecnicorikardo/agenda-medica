from __future__ import annotations

import base64
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.security import create_access_token, verify_password
from backend.app.crud.users import get_by_email
from backend.app.db.session import get_db
from backend.app.schemas.auth import LoginIn, MeOut, UsuarioOut, UsuarioPerfilUpdate
from backend.app.utils.deps import get_current_user

router = APIRouter(prefix="/auth")

# Tamanho máximo do avatar: 2MB
MAX_AVATAR_BYTES = 2 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _user_to_out(user) -> UsuarioOut:
    return UsuarioOut(
        id=user.id,
        email=user.email,
        nome=user.nome,
        crm=user.crm,
        especialidade=user.especialidade,
        telefone=user.telefone,
        email_contato=user.email_contato,
        nome_clinica=user.nome_clinica,
        avatar_url=user.avatar_url,
        lembrete_ativo=user.lembrete_ativo if user.lembrete_ativo is not None else True,
        lembrete_dias=user.lembrete_dias if user.lembrete_dias else [1],
        lembrete_msg_paciente=user.lembrete_msg_paciente,
        lembrete_msg_medico=user.lembrete_msg_medico,
    )


@router.post("/login", response_model=MeOut)
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)) -> MeOut:
    user = get_by_email(db, data.email.lower().strip())
    if not user or not verify_password(data.senha, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    if not user.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")

    settings = get_settings()
    token = create_access_token(subject=str(user.id))

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        domain=settings.auth_cookie_domain,
        path="/",
        max_age=settings.access_token_expires_minutes * 60,
    )
    return MeOut(usuario=_user_to_out(user))


@router.post("/logout")
def logout(response: Response) -> dict:
    settings = get_settings()
    response.delete_cookie(
        key=settings.auth_cookie_name,
        domain=settings.auth_cookie_domain,
        path="/",
    )
    return {"ok": True}


@router.get("/me", response_model=MeOut)
def me(user=Depends(get_current_user)) -> MeOut:
    return MeOut(usuario=_user_to_out(user))


@router.put("/perfil", response_model=MeOut)
def update_perfil(
    data: UsuarioPerfilUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> MeOut:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeOut(usuario=_user_to_out(user))


@router.post("/perfil/avatar", response_model=MeOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> MeOut:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato inválido. Use JPEG, PNG, WebP ou GIF.")

    content = await file.read()
    if len(content) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=400, detail="Imagem muito grande. Máximo 2MB.")

    # Armazena como data URL base64 (sem precisar de storage externo)
    b64 = base64.b64encode(content).decode()
    data_url = f"data:{file.content_type};base64,{b64}"

    user.avatar_url = data_url
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeOut(usuario=_user_to_out(user))


@router.delete("/perfil/avatar", response_model=MeOut)
def remove_avatar(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> MeOut:
    user.avatar_url = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeOut(usuario=_user_to_out(user))
