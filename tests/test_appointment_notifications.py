from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.app.services.appointment_notifications import (
    build_appointment_push_message,
    classify_appointment_event,
)


class AppointmentNotificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.starts_at = datetime(
            2026,
            6,
            20,
            14,
            30,
            tzinfo=ZoneInfo("America/Sao_Paulo"),
        )

    def test_classifies_every_appointment_change(self) -> None:
        self.assertEqual(classify_appointment_event({"status"}), "status_changed")
        self.assertEqual(classify_appointment_event({"inicio"}), "rescheduled")
        self.assertEqual(classify_appointment_event({"fim", "observacoes"}), "rescheduled")
        self.assertEqual(classify_appointment_event({"observacoes"}), "updated")
        self.assertIsNone(classify_appointment_event(set()))

    def test_builds_created_notification(self) -> None:
        title, body = build_appointment_push_message(
            event="created",
            patient_name="Ricardo",
            starts_at=self.starts_at,
            appointment_status="agendada",
            timezone_name="America/Sao_Paulo",
        )

        self.assertEqual(title, "Nova consulta agendada")
        self.assertEqual(body, "Ricardo • 20/06/2026 às 14:30.")

    def test_builds_whatsapp_confirmation_notification(self) -> None:
        title, body = build_appointment_push_message(
            event="status_changed",
            patient_name="Ricardo",
            starts_at=self.starts_at,
            appointment_status="confirmada",
            timezone_name="America/Sao_Paulo",
            changed_fields=("status",),
            source="whatsapp",
        )

        self.assertEqual(title, "Consulta confirmada")
        self.assertIn("confirmou", body)
        self.assertIn("pelo WhatsApp", body)

    def test_builds_cancellation_notification(self) -> None:
        title, body = build_appointment_push_message(
            event="status_changed",
            patient_name="Ricardo",
            starts_at=self.starts_at,
            appointment_status="cancelada",
            timezone_name="America/Sao_Paulo",
        )

        self.assertEqual(title, "Consulta cancelada")
        self.assertEqual(body, "Ricardo • 20/06/2026 às 14:30.")

    def test_builds_updated_notification_with_changed_fields(self) -> None:
        title, body = build_appointment_push_message(
            event="updated",
            patient_name="Ricardo",
            starts_at=self.starts_at,
            appointment_status="agendada",
            timezone_name="America/Sao_Paulo",
            changed_fields=("observacoes",),
        )

        self.assertEqual(title, "Consulta atualizada")
        self.assertIn("observações", body)


if __name__ == "__main__":
    unittest.main()
