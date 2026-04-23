from __future__ import annotations

import base64
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File, status
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


@router.post("/esqueci-senha")
async def esqueci_senha(request: Request, db: Session = Depends(get_db)) -> dict:
    """Envia e-mail com senha temporária."""
    import secrets
    from backend.app.core.security import hash_password
    from backend.app.services.email import send_email

    body = await request.json()
    email = (body.get("email") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="Informe o e-mail.")

    user = get_by_email(db, email)
    # Sempre retorna ok para não revelar se o email existe
    if not user or not user.ativo:
        return {"ok": True}

    # Gera senha temporária legível
    nova_senha = secrets.token_urlsafe(8)
    user.senha_hash = hash_password(nova_senha)
    db.add(user)
    db.commit()

    clinic = user.nome_clinica or "Agenda Médica"
    nome = user.nome or email
    html = f"""
    <!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"/>
    <style>
      body{{margin:0;padding:0;background:#f0f4ff;font-family:system-ui,sans-serif;color:#1a2540}}
      .wrap{{max-width:520px;margin:32px auto;background:#fff;border-radius:16px;
             overflow:hidden;box-shadow:0 4px 24px rgba(26,58,107,.12)}}
      .header{{background:linear-gradient(135deg,#1a3a6b,#2563eb);padding:28px 32px;text-align:center;color:#fff}}
      .header h1{{margin:0;font-size:20px;font-weight:800}}
      .body{{padding:28px 32px}}
      .senha-box{{background:#f5f8ff;border:2px solid #2563eb;border-radius:12px;
                  padding:16px 24px;text-align:center;margin:20px 0}}
      .senha{{font-size:28px;font-weight:900;letter-spacing:4px;color:#1a3a6b;font-family:monospace}}
      .footer{{background:#f5f8ff;border-top:1px solid #dce8ff;padding:14px 32px;
               text-align:center;font-size:12px;color:#8a9bbf}}
    </style></head><body>
    <div class="wrap">
      <div class="header"><h1>🏥 {clinic}</h1><p>Redefinição de senha</p></div>
      <div class="body">
        <p>Olá, <strong>{nome}</strong>!</p>
        <p>Recebemos uma solicitação de redefinição de senha para sua conta.</p>
        <p>Sua nova senha temporária é:</p>
        <div class="senha-box"><div class="senha">{nova_senha}</div></div>
        <p style="color:#6b7fa8;font-size:13px">
          Acesse o sistema e altere sua senha nas configurações de perfil.<br/>
          Se não foi você, ignore este e-mail.
        </p>
      </div>
      <div class="footer">Agenda Médica — e-mail automático</div>
    </div></body></html>
    """

    await send_email(
        to=email,
        subject=f"Sua nova senha — {clinic}",
        html=html,
    )
    return {"ok": True}


@router.post("/cadastro", response_model=MeOut)
async def cadastro(request: Request, response: Response, db: Session = Depends(get_db)) -> MeOut:
    """Cadastro de novo médico/usuário."""
    from backend.app.core.security import hash_password
    from backend.app.models.user import Usuario

    body = await request.json()
    nome  = (body.get("nome") or "").strip()
    email_val = (body.get("email") or "").lower().strip()
    senha_val = (body.get("senha") or "").strip()

    if not email_val or not senha_val:
        raise HTTPException(status_code=400, detail="E-mail e senha são obrigatórios.")
    if len(senha_val) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 6 caracteres.")

    existing = get_by_email(db, email_val)
    if existing:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    user = Usuario(
        email=email_val,
        nome=nome or None,
        senha_hash=hash_password(senha_val),
        ativo=True,
        lembrete_ativo=True,
        lembrete_dias=[1],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

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
