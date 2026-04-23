"""Script de diagnóstico — mostra o que seria enviado hoje."""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]
TZ = ZoneInfo("America/Sao_Paulo")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

with engine.connect() as conn:
    hoje = datetime.now(TZ).date()
    amanha = (datetime.now(TZ) + timedelta(days=1)).date()
    depois = (datetime.now(TZ) + timedelta(days=2)).date()

    print(f"\nHoje: {hoje}  |  Amanha: {amanha}  |  Depois: {depois}\n")

    for label, dia in [("AMANHA (--dias 1)", amanha), ("DEPOIS DE AMANHA (--dias 2)", depois)]:
        r = conn.execute(text("""
            SELECT c.id, c.inicio, c.status, p.nome_completo, p.email, p.telefone
            FROM consultas c
            JOIN pacientes p ON p.id = c.paciente_id
            WHERE DATE(c.inicio AT TIME ZONE 'America/Sao_Paulo') = :dia
              AND c.status IN ('agendada','confirmada')
            ORDER BY c.inicio
        """), {"dia": dia})
        rows = r.fetchall()
        print(f"--- {label} --- {len(rows)} consulta(s)")
        for row in rows:
            email = row[4] or "(sem email)"
            hora = row[1].astimezone(TZ).strftime("%H:%M")
            print(f"  {hora}  {row[3]:<30}  {email}")
        print()

    # Config do medico
    r2 = conn.execute(text("""
        SELECT nome, email_contato, lembrete_ativo, lembrete_dias
        FROM usuarios WHERE ativo = true
    """))
    print("--- MEDICOS ---")
    for row in r2:
        print(f"  {row[0]} | email: {row[1]} | ativo: {row[2]} | dias: {row[3]}")
