"""
Script para popular o banco com dados fictícios:
- 30 pacientes
- ~20 consultas distribuídas nos próximos 7 dias
"""
from __future__ import annotations

import os
import random
import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise SystemExit("Defina DATABASE_URL no .env")

TZ = ZoneInfo("America/Sao_Paulo")

NOMES = [
    "Ana Clara Souza", "Bruno Henrique Lima", "Carla Mendes Oliveira",
    "Diego Ferreira Santos", "Elaine Costa Pereira", "Fábio Rodrigues Alves",
    "Gabriela Martins Silva", "Henrique Barbosa Nunes", "Isabela Carvalho Rocha",
    "João Pedro Gomes", "Karina Nascimento Dias", "Leonardo Araújo Moreira",
    "Mariana Lopes Cardoso", "Nicolas Ribeiro Teixeira", "Olivia Pinto Monteiro",
    "Paulo Cesar Vieira", "Queila Fernandes Borges", "Rafael Cunha Azevedo",
    "Sabrina Torres Melo", "Thiago Batista Correia", "Ursula Campos Freitas",
    "Vitor Hugo Peixoto", "Wanda Moura Cavalcanti", "Xavier Duarte Fonseca",
    "Yasmin Andrade Macedo", "Zeca Nogueira Sampaio", "Alice Ramos Guimaraes",
    "Bernardo Sousa Lacerda", "Cecilia Vaz Drummond", "Daniel Queiroz Esteves",
]

TELEFONES = [
    f"(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    for _ in range(30)
]

EMAILS = [
    f"{nome.split()[0].lower()}.{nome.split()[-1].lower()}@email.com"
    for nome in NOMES
]

OBSERVACOES = [
    "Hipertensão controlada", "Diabético tipo 2", "Alergia a penicilina",
    "Histórico de asma", "Sem observações", None, "Gestante - 2º trimestre",
    "Pós-operatório de apendicite", "Ansiedade e insônia", "Hipotireoidismo",
]


def main() -> None:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    with Session(engine) as db:
        # Pega o primeiro usuário cadastrado
        row = db.execute(text("SELECT id FROM usuarios LIMIT 1")).fetchone()
        if not row:
            raise SystemExit("Nenhum usuário encontrado. Rode create_user.py primeiro.")
        usuario_id = row[0]
        print(f"Usando usuário: {usuario_id}")

        # Cria 30 pacientes
        paciente_ids = []
        for i, nome in enumerate(NOMES):
            pid = uuid.uuid4()
            nascimento = date(
                random.randint(1950, 2005),
                random.randint(1, 12),
                random.randint(1, 28),
            )
            db.execute(text("""
                INSERT INTO pacientes (id, usuario_id, nome_completo, telefone, email, data_nascimento, observacoes)
                VALUES (:id, :uid, :nome, :tel, :email, :nasc, :obs)
                ON CONFLICT DO NOTHING
            """), {
                "id": str(pid),
                "uid": str(usuario_id),
                "nome": nome,
                "tel": f"(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "email": EMAILS[i],
                "nasc": nascimento,
                "obs": random.choice(OBSERVACOES),
            })
            paciente_ids.append(pid)
            print(f"  Paciente criado: {nome}")

        db.commit()
        print(f"\n30 pacientes criados!")

        # Cria ~20 consultas nos próximos 7 dias
        hoje = datetime.now(TZ).date()
        status_opcoes = ["agendada", "confirmada", "agendada", "agendada", "confirmada"]
        horarios = [time(8,0), time(8,30), time(9,0), time(9,30), time(10,0),
                    time(10,30), time(11,0), time(14,0), time(14,30), time(15,0),
                    time(15,30), time(16,0), time(16,30), time(17,0), time(17,30)]

        consultas_criadas = 0
        slots_usados = set()

        for paciente_id in random.sample(paciente_ids, 20):
            dia = hoje + timedelta(days=random.randint(0, 7))
            horario = random.choice(horarios)
            slot_key = (dia, horario)
            if slot_key in slots_usados:
                continue
            slots_usados.add(slot_key)

            inicio = datetime.combine(dia, horario, tzinfo=TZ)
            fim = inicio + timedelta(minutes=30)

            db.execute(text("""
                INSERT INTO consultas (id, usuario_id, paciente_id, inicio, fim, status)
                VALUES (:id, :uid, :pid, :inicio, :fim, :status)
                ON CONFLICT DO NOTHING
            """), {
                "id": str(uuid.uuid4()),
                "uid": str(usuario_id),
                "pid": str(paciente_id),
                "inicio": inicio,
                "fim": fim,
                "status": random.choice(status_opcoes),
            })
            consultas_criadas += 1

        db.commit()
        print(f"{consultas_criadas} consultas criadas nos próximos 7 dias!")
        print("\nPronto! Recarregue o sistema.")


if __name__ == "__main__":
    main()
