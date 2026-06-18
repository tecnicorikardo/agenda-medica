from __future__ import annotations

import asyncio
import logging

from backend.app.db.session import SessionLocal
from backend.app.services.whatsapp_reminders import process_automatic_whatsapp_reminders

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    with SessionLocal() as db:
        stats = await process_automatic_whatsapp_reminders(db)
    print(
        "Lembretes WhatsApp concluídos: "
        f"{stats['enviados']} enviados, "
        f"{stats['ignorados']} ignorados, "
        f"{stats['erros']} erros."
    )


if __name__ == "__main__":
    asyncio.run(main())
