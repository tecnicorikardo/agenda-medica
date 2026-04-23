"""Redefine a senha de um usuário pelo e-mail."""
from dotenv import load_dotenv
load_dotenv()
import sys, os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from backend.app.models.user import Usuario
from backend.app.core.security import hash_password

email = sys.argv[1] if len(sys.argv) > 1 else input("E-mail: ").strip()
nova  = sys.argv[2] if len(sys.argv) > 2 else input("Nova senha: ").strip()

engine = create_engine(os.environ["DATABASE_URL"])
with Session(engine) as db:
    user = db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if not user:
        print(f"Usuário '{email}' não encontrado.")
        sys.exit(1)
    user.senha_hash = hash_password(nova)
    db.add(user)
    db.commit()
    print(f"✅ Senha de '{email}' atualizada com sucesso.")
