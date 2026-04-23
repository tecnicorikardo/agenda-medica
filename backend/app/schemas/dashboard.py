from __future__ import annotations

from datetime import date, datetime

from backend.app.schemas.base import APIModel

from backend.app.schemas.appointment import ConsultaWithPaciente


class SlotLivre(APIModel):
    inicio: datetime
    fim: datetime


class DashboardOut(APIModel):
    dia: date
    consultas_do_dia: int
    proximo_paciente: ConsultaWithPaciente | None
    horarios_livres: list[SlotLivre]
    pacientes_cadastrados: int
    consultas_canceladas: int
    atendimentos_concluidos: int
