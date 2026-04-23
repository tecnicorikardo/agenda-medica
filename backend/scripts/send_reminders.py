"""
Script de disparo de lembretes via WhatsApp (1 dia antes da consulta).

Uso:
    python -m backend.scripts.send_reminders

O que faz:
  1. Busca consultas de amanhã com status agendada/confirmada
  2. Para cada uma, gera link wa.me com mensagem pré-formatada
  3. Registra na tabela lembretes (status=pendente, canal=whatsapp)
  4. Abre os links no browser para envio manual
     (ou use WHATSAPP_AUTO=true + Z-API/Twilio para envio automático)

Variáveis de ambiente opcionais:
    CLINIC_NAME   - Nome do consultório (padrão: "Agenda Médica")
    DOCTOR_NAME   - Nome do médico (padrão: "")
"""
from __future__ import annotations

import os
import sys
import uuid
import webbrowser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise SystemExit("Defina DATABASE_URL no .env")

CLINIC_NAME = os.environ.get("CLINIC_NAME", "Agenda Médica")
DOCTOR_NAME = os.environ.get("DOCTOR_NAME", "")
TZ = ZoneInfo("America/Sao_Paulo")


def _limpar_telefone(tel: str) -> str:
    """Remove tudo que não é dígito e garante código do país 55."""
    digits = "".join(c for c in tel if c.isdigit())
    if not digits.startswith("55"):
        digits = "55" + digits
    return digits


def _montar_mensagem(nome: str, inicio: datetime, clinic: str, doctor: str) -> str:
    data_str = inicio.astimezone(TZ).strftime("%d/%m/%Y")
    hora_str = inicio.astimezone(TZ).strftime("%H:%M")
    medico_str = f" com {doctor}" if doctor else ""
    return (
        f"Olá, {nome.split()[0]}! 👋\n\n"
        f"Lembramos que você tem uma consulta{medico_str} amanhã, "
        f"*{data_str}* às *{hora_str}*.\n\n"
        f"📍 {clinic}\n\n"
        f"Confirme sua presença respondendo esta mensagem. "
        f"Caso precise remarcar, entre em contato com antecedência.\n\n"
        f"Até amanhã! 😊"
    )


def main() -> None:
    from urllib.parse import quote

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    with Session(engine) as db:
        # Importa modelos aqui para evitar problemas de path
        from backend.app.models.appointment import Consulta
        from backend.app.models.patient import Paciente
        from backend.app.models.reminder import Lembrete

        agora = datetime.now(TZ)
        amanha_inicio = datetime.combine(
            (agora + timedelta(days=1)).date(),
            __import__("datetime").time.min,
            tzinfo=TZ,
        )
        amanha_fim = amanha_inicio + timedelta(days=1)

        consultas = list(db.scalars(
            select(Consulta)
            .where(and_(
                Consulta.inicio >= amanha_inicio,
                Consulta.inicio < amanha_fim,
                Consulta.status.in_(["agendada", "confirmada"]),
            ))
            .order_by(Consulta.inicio.asc())
        ).all())

        if not consultas:
            print("Nenhuma consulta encontrada para amanhã.")
            return

        print(f"\n{len(consultas)} consulta(s) encontrada(s) para amanhã:\n")

        links = []
        for c in consultas:
            paciente = db.get(Paciente, c.paciente_id)
            if not paciente:
                print(f"  [SKIP] Consulta {c.id} sem paciente vinculado.")
                continue

            tel = _limpar_telefone(paciente.telefone or "")
            if len(tel) < 12:
                print(f"  [SKIP] {paciente.nome_completo} — telefone inválido: {paciente.telefone}")
                continue

            msg = _montar_mensagem(paciente.nome_completo, c.inicio, CLINIC_NAME, DOCTOR_NAME)
            link = f"https://wa.me/{tel}?text={quote(msg)}"

            hora = c.inicio.astimezone(TZ).strftime("%H:%M")
            print(f"  ✅ {hora} — {paciente.nome_completo} ({paciente.telefone})")
            print(f"     {link[:80]}...")

            # Registra lembrete na tabela
            lembrete = Lembrete(
                id=uuid.uuid4(),
                consulta_id=c.id,
                canal="whatsapp",
                agendado_para=agora,
                status="pendente",
                payload={"link": link, "telefone": tel, "nome": paciente.nome_completo},
            )
            db.add(lembrete)
            links.append((paciente.nome_completo, link))

        db.commit()
        print(f"\n{len(links)} lembrete(s) registrado(s) no banco.")

        if not links:
            return

        resp = input("\nAbrir links no WhatsApp Web agora? (s/N): ").strip().lower()
        if resp == "s":
            for nome, link in links:
                print(f"  Abrindo para {nome}...")
                webbrowser.open(link)
            print("\nPronto! Confirme o envio no WhatsApp Web.")
        else:
            print("\nLinks salvos no banco. Rode novamente quando quiser abrir.")


if __name__ == "__main__":
    main()
