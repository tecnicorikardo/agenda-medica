"""
Verifica o status dos templates do WhatsApp Business.

Uso:
    python -m backend.scripts.check_whatsapp_templates

Requer no ambiente:
    WHATSAPP_ACCESS_TOKEN
    WHATSAPP_PHONE_NUMBER_ID
    WHATSAPP_BUSINESS_ACCOUNT_ID
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

import aiohttp
from dotenv import load_dotenv

load_dotenv()


def _api_version() -> str:
    return (os.environ.get("WHATSAPP_API_VERSION") or "v20.0").strip().strip("/")


def _required_env(name: str) -> str:
    value = (os.environ.get(name) or "").strip()
    if not value:
        raise RuntimeError(f"Configure {name} no ambiente.")
    return value


async def _get_json(session: aiohttp.ClientSession, url: str, headers: dict[str, str]) -> dict[str, Any]:
    async with session.get(url, headers=headers) as resp:
        body = await resp.text()
        if resp.status != 200:
            raise RuntimeError(f"Erro {resp.status} em {url}: {body}")
        return await resp.json()


async def _list_templates(
    session: aiohttp.ClientSession,
    *,
    api_version: str,
    business_account_id: str,
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    templates: list[dict[str, Any]] = []
    url = (
        f"https://graph.facebook.com/{api_version}/{business_account_id}/message_templates"
        "?fields=name,status,category,language,components&limit=100"
    )

    while url:
        data = await _get_json(session, url, headers)
        templates.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")

    return templates


def _status_emoji(status: str) -> str:
    return {
        "APPROVED": "OK",
        "PENDING": "PENDENTE",
        "REJECTED": "REJEITADO",
        "DISABLED": "DESATIVADO",
    }.get(status, "DESCONHECIDO")


def _body_preview(template: dict[str, Any]) -> str:
    for component in template.get("components", []):
        if component.get("type") == "BODY":
            return (component.get("text") or "").replace("\n", " ")[:120]
    return ""


def _validate_configured_template(
    *,
    label: str,
    name: str,
    language: str,
    templates: list[dict[str, Any]],
) -> None:
    if not name:
        print(f"AVISO: {label} sem template configurado.")
        return

    matches = [t for t in templates if t.get("name") == name]
    if not matches:
        print(f"ERRO: {label} '{name}' não existe nesta conta WhatsApp Business.")
        return

    language_matches = [t for t in matches if t.get("language") == language]
    if not language_matches:
        languages = ", ".join(sorted({str(t.get("language")) for t in matches}))
        print(f"ERRO: {label} '{name}' existe, mas não no idioma {language}. Idiomas: {languages}")
        return

    approved = [t for t in language_matches if t.get("status") == "APPROVED"]
    if approved:
        print(f"OK: {label} '{name}' aprovado em {language}.")
        return

    statuses = ", ".join(sorted({str(t.get("status")) for t in language_matches}))
    print(f"AGUARDANDO: {label} '{name}' em {language} está com status: {statuses}.")


async def check_templates() -> None:
    try:
        access_token = _required_env("WHATSAPP_ACCESS_TOKEN")
        phone_number_id = _required_env("WHATSAPP_PHONE_NUMBER_ID")
        business_account_id = _required_env("WHATSAPP_BUSINESS_ACCOUNT_ID")
    except RuntimeError as exc:
        print(f"ERRO: {exc}")
        return

    api_version = _api_version()
    language = (os.environ.get("WHATSAPP_TEMPLATE_LANGUAGE") or "pt_BR").strip()
    patient_template = (os.environ.get("WHATSAPP_PATIENT_TEMPLATE_NAME") or "").strip()
    doctor_template = (os.environ.get("WHATSAPP_DOCTOR_TEMPLATE_NAME") or "").strip()
    headers = {"Authorization": f"Bearer {access_token}"}

    async with aiohttp.ClientSession() as session:
        print("Verificando número do WhatsApp...")
        phone_url = (
            f"https://graph.facebook.com/{api_version}/{phone_number_id}"
            "?fields=id,display_phone_number,verified_name"
        )
        phone_data = await _get_json(session, phone_url, headers)
        print(
            "OK: "
            f"{phone_data.get('verified_name', '-')}"
            f" ({phone_data.get('display_phone_number', '-')})"
            f" / Phone Number ID {phone_data.get('id', phone_number_id)}"
        )

        print("\nBuscando templates na Conta WhatsApp Business...")
        templates = await _list_templates(
            session,
            api_version=api_version,
            business_account_id=business_account_id,
            headers=headers,
        )

    if not templates:
        print("Nenhum template encontrado nesta Conta WhatsApp Business.")
        return

    print(f"\n{len(templates)} template(s) encontrado(s):\n")
    for index, template in enumerate(templates, 1):
        print(f"{index}. {template.get('name')}")
        print(f"   Status:    {_status_emoji(str(template.get('status', '')))} ({template.get('status')})")
        print(f"   Categoria: {template.get('category')}")
        print(f"   Idioma:    {template.get('language')}")
        preview = _body_preview(template)
        if preview:
            print(f"   Conteúdo:  {preview}...")
        print()

    print("Configuração atual:")
    print(f"   WHATSAPP_BUSINESS_ACCOUNT_ID: {business_account_id}")
    print(f"   WHATSAPP_PHONE_NUMBER_ID:     {phone_number_id}")
    print(f"   WHATSAPP_TEMPLATE_LANGUAGE:   {language}")
    print(f"   WHATSAPP_PATIENT_TEMPLATE:    {patient_template or '-'}")
    print(f"   WHATSAPP_DOCTOR_TEMPLATE:     {doctor_template or '-'}")

    print("\nValidação:")
    _validate_configured_template(
        label="Paciente",
        name=patient_template,
        language=language,
        templates=templates,
    )
    _validate_configured_template(
        label="Médico",
        name=doctor_template,
        language=language,
        templates=templates,
    )


if __name__ == "__main__":
    print("Verificador de Templates do WhatsApp Business")
    print("=" * 60)
    asyncio.run(check_templates())
    print("=" * 60)
