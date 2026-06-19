"""Cria ou atualiza o usuário de teste para os testes Playwright."""
import os
import sys
import uuid

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def main() -> None:
    from backend.app.core.security import hash_password

    load_dotenv()
    test_email = "playwright.teste@gmail.com"
    test_password = "Playwright@2026"

    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        raise SystemExit("DATABASE_URL não configurado no .env")

    engine = create_engine(db_url, pool_pre_ping=True)
    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT id FROM usuarios WHERE email = :e"),
            {"e": test_email},
        ).fetchone()

        if exists:
            conn.execute(
                text("UPDATE usuarios SET senha_hash=:h, ativo=true WHERE email=:e"),
                {"h": hash_password(test_password), "e": test_email},
            )
            print(f"✅ Usuário de teste atualizado: {test_email}")
        else:
            conn.execute(
                text("""
                    INSERT INTO usuarios (
                        id, email, nome, senha_hash, ativo, lembrete_ativo, lembrete_dias
                    )
                    VALUES (:id, :email, :nome, :hash, true, true, ARRAY[1]::integer[])
                """),
                {
                    "id": str(uuid.uuid4()),
                    "email": test_email,
                    "nome": "Dr. Playwright Teste",
                    "hash": hash_password(test_password),
                },
            )
            print(f"✅ Usuário de teste criado: {test_email}")

    print(f"   Senha: {test_password}")
    print("\nAdicione ao .env ou use diretamente:")
    print(f"TEST_EMAIL={test_email}")
    print(f"TEST_PASSWORD={test_password}")


if __name__ == "__main__":
    main()
