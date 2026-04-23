from __future__ import annotations

from backend.app.schemas.appointment import ConsultaOut
from backend.app.schemas.base import APIModel
from backend.app.schemas.patient import PacienteDetail


class HistoricoPacienteOut(APIModel):
    paciente: PacienteDetail
    consultas: list[ConsultaOut]

