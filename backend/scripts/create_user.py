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


def _mask_database_url(database_url: str) -> str:
    try:
        url = make_url(database_url)
        if url.password:
            url = url.set(password="***")
        return str(url)
    except Exception:
        # fallback: avoid printing secrets
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

    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with Session(engine) as db:
            exists = db.query(Usuario).filter(Usuario.email == email).first()
            if exists:
                raise SystemExit("Já existe um usuário com esse e-mail.")
            user = Usuario(email=email, nome=nome, senha_hash=hash_password(senha), ativo=True)
            db.add(user)
            db.commit()
            print(f"Usuário criado: {user.id}")
    except UnicodeDecodeError:
        masked = _mask_database_url(database_url)
        print("Falha ao conectar no Postgres (UnicodeDecodeError).", file=sys.stderr)
        print(f"DATABASE_URL (mascarada): {masked}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Causa mais comum: senha do Postgres com caracteres especiais não URL-encodados.", file=sys.stderr)
        print("Exemplos de caracteres que exigem encoding: @ : / ? # & espaço e acentos.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Como corrigir:", file=sys.stderr)
        print("1) Pegue sua senha do Postgres do Supabase (sem alterar)", file=sys.stderr)
        print("2) Gere a versão URL-encoded e use no DATABASE_URL", file=sys.stderr)
        print("", file=sys.stderr)
        print("One-liner (substitua SUA_SENHA):", file=sys.stderr)
        print(r'python -c "import urllib.parse; print(urllib.parse.quote_plus(\'SUA_SENHA\'))"', file=sys.stderr)
        raise SystemExit(2)
    except OperationalError as exc:
        masked = _mask_database_url(database_url)
        print("Falha ao conectar no Postgres (OperationalError).", file=sys.stderr)
        print(f"DATABASE_URL (mascarada): {masked}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Dicas:", file=sys.stderr)
        print("- Confirme se o SQL do `docs/supabase_schema.sql` foi executado no Supabase.", file=sys.stderr)
        print("- Verifique host/porta/usuário/senha no `DATABASE_URL`.", file=sys.stderr)
        print("- Se a senha tiver caracteres especiais, URL-encode (veja acima).", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
