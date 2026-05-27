"""
Cria o primeiro usuário (médico) no banco de dados.

Uso:
    python -m backend.scripts.create_user

Pré-requisito: DATABASE_URL definida no .env ou no ambiente.
As tabelas são criadas automaticamente via migrations (Alembic).
"""
from __future__ import annotations

import getpass
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.user import Usuario


def _mask_url(database_url: str) -> str:
    try:
        url = make_url(database_url)
        if url.password:
            url = url.set(password="***")
        return str(url)
    except Exception:
        if "@" in database_url:
            left, right = database_url.split("@", 1)
            return left.split(":", 1)[0] + ":***@" + right
        return database_url[:30] + "…"


def main() -> None:
    load_dotenv()
    database_url = (os.environ.get("DATABASE_URL") or "").strip().strip('"').strip("'")
    if not database_url:
        raise SystemExit("Defina DATABASE_URL no ambiente (.env) antes de rodar este script.")

    email = input("E-mail: ").strip().lower()
    nome = input("Nome (opcional): ").strip() or None
    senha = getpass.getpass("Senha: ")
    senha2 = getpass.getpass("Confirmar senha: ")
    if senha != senha2:
        raise SystemExit("Senhas não conferem.")
    if len(senha) < 6:
        raise SystemExit("Senha deve ter pelo menos 6 caracteres.")

    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with Session(engine) as db:
            exists = db.query(Usuario).filter(Usuario.email == email).first()
            if exists:
                raise SystemExit("Já existe um usuário com esse e-mail.")
            user = Usuario(
                email=email,
                nome=nome,
                senha_hash=hash_password(senha),
                ativo=True,
                lembrete_ativo=True,
                lembrete_dias=[1],
            )
            db.add(user)
            db.commit()
            print(f"\n✅ Usuário criado com sucesso!")
            print(f"   ID:    {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Nome:  {user.nome or '(não informado)'}")
    except OperationalError as exc:
        masked = _mask_url(database_url)
        print(f"\n❌ Falha ao conectar no banco de dados.", file=sys.stderr)
        print(f"   DATABASE_URL: {masked}", file=sys.stderr)
        print(f"\nDicas:", file=sys.stderr)
        print(f"  - Verifique se o banco está acessível e as credenciais estão corretas.", file=sys.stderr)
        print(f"  - Se a senha tiver caracteres especiais (@, :, espaço), use URL-encoding:", file=sys.stderr)
        print(f'    python -c "import urllib.parse; print(urllib.parse.quote_plus(\'SUA_SENHA\'))"', file=sys.stderr)
        print(f"  - Certifique-se de rodar as migrations antes: python -m backend.scripts.migrate", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
