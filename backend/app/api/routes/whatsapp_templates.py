from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.schemas.whatsapp import (
    TipoTemplateWhatsApp,
    WhatsAppTemplateOut,
    WhatsAppTemplatePreview,
    WhatsAppTemplatePreviewOut,
    WhatsAppTemplateUpdate,
)
from backend.app.services.whatsapp_content import (
    DEFAULT_TEMPLATES,
    TIPOS_TEMPLATE,
    TemplateContext,
    get_template,
    render_template,
    reset_template,
    upsert_template,
)
from backend.app.utils.deps import get_current_user

router = APIRouter(prefix="/whatsapp/templates", tags=["whatsapp"])


def _serialize(user, tipo: str, template=None) -> WhatsAppTemplateOut:
    default = DEFAULT_TEMPLATES[tipo]
    return WhatsAppTemplateOut(
        id=template.id if template else None,
        medico_id=user.id,
        nome=template.nome if template else default["nome"],
        tipo=tipo,
        conteudo=template.conteudo if template else default["conteudo"],
        ativo=template.ativo if template else True,
        padrao=default["conteudo"],
        created_at=template.created_at if template else None,
        updated_at=template.updated_at if template else None,
    )


def _preview_context(user) -> TemplateContext:
    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone)
    return TemplateContext(
        paciente="Maria da Silva",
        medico=user.nome or "João Souza",
        inicio=datetime.now(tz) + timedelta(days=1, hours=2),
        clinica=user.nome_clinica or "Clínica Exemplo",
        telefone=user.telefone or "(11) 99999-9999",
        timezone=tz,
    )


@router.get("", response_model=list[WhatsAppTemplateOut])
def list_templates(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[WhatsAppTemplateOut]:
    return [
        _serialize(user, tipo, get_template(db, medico_id=user.id, tipo=tipo))
        for tipo in TIPOS_TEMPLATE
    ]


@router.put("/{tipo}", response_model=WhatsAppTemplateOut)
def update_template(
    tipo: TipoTemplateWhatsApp,
    data: WhatsAppTemplateUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> WhatsAppTemplateOut:
    try:
        template = upsert_template(
            db,
            medico_id=user.id,
            tipo=tipo,
            nome=data.nome,
            conteudo=data.conteudo,
            ativo=data.ativo,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _serialize(user, tipo, template)


@router.post("/{tipo}/reset", response_model=WhatsAppTemplateOut)
def restore_template(
    tipo: TipoTemplateWhatsApp,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> WhatsAppTemplateOut:
    template = reset_template(db, medico_id=user.id, tipo=tipo)
    return _serialize(user, tipo, template)


@router.post("/preview", response_model=WhatsAppTemplatePreviewOut)
def preview_template(
    data: WhatsAppTemplatePreview,
    user=Depends(get_current_user),
) -> WhatsAppTemplatePreviewOut:
    try:
        content = render_template(data.conteudo, _preview_context(user))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WhatsAppTemplatePreviewOut(conteudo=content)
