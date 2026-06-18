from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.app.models.whatsapp_template import TemplateWhatsApp

TIPOS_TEMPLATE = ("lembrete", "confirmacao", "cancelamento")
VARIAVEIS_SUPORTADAS = {
    "paciente",
    "medico",
    "data",
    "hora",
    "data_hora",
    "clinica",
    "telefone",
}

DEFAULT_TEMPLATES = {
    "lembrete": {
        "nome": "Lembrete de consulta",
        "conteudo": (
            "Olá {paciente}.\n\n"
            "Sua consulta com Dr(a). {medico} está marcada para {data_hora}.\n\n"
            "Confirme sua presença usando uma das opções abaixo."
        ),
    },
    "confirmacao": {
        "nome": "Confirmação de consulta",
        "conteudo": (
            "Olá {paciente}! Sua consulta com Dr(a). {medico} em {data_hora} "
            "foi confirmada. Até lá!"
        ),
    },
    "cancelamento": {
        "nome": "Cancelamento de consulta",
        "conteudo": (
            "Olá {paciente}. Sua consulta com Dr(a). {medico} em {data_hora} "
            "foi cancelada. Entre em contato com {telefone} para reagendar."
        ),
    },
}

_VARIABLE_PATTERN = re.compile(r"\{([a-z_]+)\}")


@dataclass(frozen=True)
class TemplateContext:
    paciente: str
    medico: str
    inicio: datetime
    clinica: str
    telefone: str
    timezone: ZoneInfo

    def values(self) -> dict[str, str]:
        inicio_local = self.inicio.astimezone(self.timezone)
        data = inicio_local.strftime("%d/%m/%Y")
        hora = inicio_local.strftime("%H:%M")
        return {
            "paciente": self.paciente,
            "medico": self.medico,
            "data": data,
            "hora": hora,
            "data_hora": f"{data} às {hora}",
            "clinica": self.clinica,
            "telefone": self.telefone,
        }


def validate_template_content(content: str) -> str:
    normalized = content.strip()
    if not normalized:
        raise ValueError("O conteúdo do template não pode ficar vazio.")
    if len(normalized) > 4096:
        raise ValueError("O conteúdo do template deve ter no máximo 4096 caracteres.")

    unknown = sorted(set(_VARIABLE_PATTERN.findall(normalized)) - VARIAVEIS_SUPORTADAS)
    if unknown:
        variables = ", ".join(f"{{{name}}}" for name in unknown)
        raise ValueError(f"Variáveis não suportadas: {variables}.")
    return normalized


def render_template(content: str, context: TemplateContext) -> str:
    rendered = validate_template_content(content)
    for name, value in context.values().items():
        rendered = rendered.replace(f"{{{name}}}", value)
    return rendered


def get_template(
    db: Session,
    *,
    medico_id,
    tipo: str,
) -> TemplateWhatsApp | None:
    if tipo not in TIPOS_TEMPLATE:
        raise ValueError("Tipo de template inválido.")
    return db.scalar(
        select(TemplateWhatsApp).where(
            and_(
                TemplateWhatsApp.medico_id == medico_id,
                TemplateWhatsApp.tipo == tipo,
            )
        )
    )


def get_template_content(db: Session, *, medico_id, tipo: str) -> str:
    template = get_template(db, medico_id=medico_id, tipo=tipo)
    if template and template.ativo:
        return template.conteudo
    return DEFAULT_TEMPLATES[tipo]["conteudo"]


def upsert_template(
    db: Session,
    *,
    medico_id,
    tipo: str,
    conteudo: str,
    ativo: bool = True,
    nome: str | None = None,
) -> TemplateWhatsApp:
    if tipo not in TIPOS_TEMPLATE:
        raise ValueError("Tipo de template inválido.")

    template = get_template(db, medico_id=medico_id, tipo=tipo)
    if template is None:
        template = TemplateWhatsApp(
            medico_id=medico_id,
            tipo=tipo,
            nome=nome or DEFAULT_TEMPLATES[tipo]["nome"],
            conteudo=validate_template_content(conteudo),
            ativo=ativo,
        )
    else:
        template.nome = nome or template.nome
        template.conteudo = validate_template_content(conteudo)
        template.ativo = ativo

    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def reset_template(db: Session, *, medico_id, tipo: str) -> TemplateWhatsApp:
    default = DEFAULT_TEMPLATES.get(tipo)
    if not default:
        raise ValueError("Tipo de template inválido.")
    return upsert_template(
        db,
        medico_id=medico_id,
        tipo=tipo,
        nome=default["nome"],
        conteudo=default["conteudo"],
        ativo=True,
    )
