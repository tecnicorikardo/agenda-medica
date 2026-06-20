from __future__ import annotations

import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from backend.app.services.email_templates import (
    confirmacao_agendamento_paciente_html,
    lembrete_paciente_html,
)


class PatientEmailTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inicio = datetime(
            2026,
            6,
            22,
            14,
            30,
            tzinfo=ZoneInfo("America/Sao_Paulo"),
        )
        self.fim = self.inicio + timedelta(minutes=30)

    def test_reminder_contains_confirmation_email_action(self) -> None:
        _, html = lembrete_paciente_html(
            paciente_nome="Ricardo Martins Santos",
            inicio=self.inicio,
            fim=self.fim,
            dias_antes=1,
            clinic_name="Clínica Vida",
            doctor_name="Marina Silva",
            doctor_email="medica@example.com",
        )

        self.assertIn("Confirmar presença por e-mail", html)
        self.assertIn("mailto:medica@example.com?", html)
        self.assertIn("Ricardo%20Martins%20Santos", html)
        self.assertIn("22%2F06%2F2026", html)
        self.assertIn("14%3A30", html)

    def test_scheduling_confirmation_contains_confirmation_email_action(self) -> None:
        _, html = confirmacao_agendamento_paciente_html(
            paciente_nome="Ricardo Martins Santos",
            inicio=self.inicio,
            fim=self.fim,
            clinic_name="Clínica Vida",
            doctor_name="Marina Silva",
            doctor_email="medica@example.com",
        )

        self.assertIn("Confirmar presença por e-mail", html)
        self.assertIn("mailto:medica@example.com?", html)

    def test_email_action_is_omitted_without_doctor_email(self) -> None:
        _, html = lembrete_paciente_html(
            paciente_nome="Ricardo Martins Santos",
            inicio=self.inicio,
            fim=self.fim,
            dias_antes=1,
            clinic_name="Clínica Vida",
            doctor_name="Marina Silva",
        )

        self.assertNotIn("Confirmar presença por e-mail", html)


if __name__ == "__main__":
    unittest.main()
