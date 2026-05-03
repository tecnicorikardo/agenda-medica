"""Cria ou atualiza o usuário de teste para os testes Playwright."""
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from backend.app.core.security import hash_password

TEST_EMAIL = "playwright.teste@gmail.com"
TEST_PASS  = "Playwright@2026"

db_url = os.environ.get("DATABASE_URL", "")
if not db_url:
    raise SystemExit("DATABASE_URL não configurado no .env")

engine = create_engine(db_url, pool_pre_ping=True)

with engine.begin() as conn:
    exists = conn.execute(
        text("SELECT id FROM usuarios WHERE email = :e"),
        {"e": TEST_EMAIL}
    ).fetchone()

    if exists:
        conn.execute(
            text("UPDATE usuarios SET senha_hash=:h, ativo=true WHERE email=:e"),
            {"h": hash_password(TEST_PASS), "e": TEST_EMAIL}
        )
        print(f"✅ Usuário de teste atualizado: {TEST_EMAIL}")
    else:
        conn.execute(
            text("""
                INSERT INTO usuarios (id, email, nome, senha_hash, ativo, lembrete_ativo, lembrete_dias)
                VALUES (:id, :email, :nome, :hash, true, true, ARRAY[1]::integer[])
            """),
            {
                "id": str(uuid.uuid4()),
                "email": TEST_EMAIL,
                "nome": "Dr. Playwright Teste",
                "hash": hash_password(TEST_PASS),
            }
        )
        print(f"✅ Usuário de teste criado: {TEST_EMAIL}")

print(f"   Senha: {TEST_PASS}")
print(f"\nAdicione ao .env ou use diretamente:")
print(f"TEST_EMAIL={TEST_EMAIL}")
print(f"TEST_PASSWORD={TEST_PASS}")
