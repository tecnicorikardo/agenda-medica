"""
Roda as migrations do Alembic (upgrade head).
Usado no startup do container antes de subir o uvicorn.

Uso:
    python -m backend.scripts.migrate
"""
from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    # Localiza alembic.ini na raiz do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))

    # Garante que o DATABASE_URL está setado
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        logger.error("DATABASE_URL não definida — abortando migrations.")
        sys.exit(1)

    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))

    logger.info("Rodando migrations (alembic upgrade head)...")
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations concluídas.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run_migrations()
