"""Remove lembretes de teste para permitir reenvio."""
from dotenv import load_dotenv
load_dotenv()
import os
from sqlalchemy import create_engine, text

engine = create_engine(os.environ["DATABASE_URL"])
with engine.begin() as conn:
    r = conn.execute(text("DELETE FROM lembretes WHERE canal IN ('email', 'email_medico')"))
    print(f"Lembretes removidos: {r.rowcount}")
