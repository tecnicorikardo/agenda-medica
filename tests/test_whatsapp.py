from __future__ import annotations

import hashlib
import hmac
import unittest
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from backend.app.services.whatsapp_content import (
    TemplateContext,
    render_template,
    validate_template_content,
)
from backend.app.services.whatsapp_templates import (
    WhatsAppReminder,
    patient_template_parameters,
)
from backend.app.services.whatsapp_webhook import (
    extract_button_action,
    iter_webhook_events,
    verify_whatsapp_signature,
)


class WhatsAppContentTests(unittest.TestCase):
    def test_render_supported_variables(self) -> None:
        context = TemplateContext(
            paciente="Maria",
            medico="João",
            inicio=datetime(2026, 6, 20, 14, 30, tzinfo=ZoneInfo("America/Sao_Paulo")),
            clinica="Clínica Central",
            telefone="11999999999",
            timezone=ZoneInfo("America/Sao_Paulo"),
        )

        rendered = render_template(
            "{paciente} | {medico} | {data} | {hora} | {data_hora} | {clinica} | {telefone}",
            context,
        )

        self.assertEqual(
            rendered,
            "Maria | João | 20/06/2026 | 14:30 | 20/06/2026 às 14:30 | "
            "Clínica Central | 11999999999",
        )

    def test_reject_unknown_variable(self) -> None:
        with self.assertRaisesRegex(ValueError, "Variáveis não suportadas"):
            validate_template_content("Olá {convenio}")

    def test_template_parameter_modes(self) -> None:
        reminder = WhatsAppReminder(body="Mensagem", template_parameters=["Maria", "20/06/2026"])

        self.assertEqual(
            patient_template_parameters(
                reminder,
                rendered_body="Conteúdo personalizado",
                parameter_mode="message",
            ),
            ["Conteúdo personalizado"],
        )
        self.assertEqual(
            patient_template_parameters(
                reminder,
                rendered_body="Conteúdo personalizado",
                parameter_mode="standard",
            ),
            ["Maria", "20/06/2026"],
        )


class WhatsAppWebhookTests(unittest.TestCase):
    def test_extract_template_button_action(self) -> None:
        appointment_id = uuid4()
        action, parsed_id, context_id = extract_button_action({
            "type": "button",
            "button": {
                "payload": f"confirmar:{appointment_id}",
                "text": "Confirmar Consulta",
            },
            "context": {"id": "wamid.outgoing"},
        })

        self.assertEqual(action, "confirmar")
        self.assertEqual(parsed_id, appointment_id)
        self.assertEqual(context_id, "wamid.outgoing")

    def test_extract_interactive_cancel_action(self) -> None:
        appointment_id = uuid4()
        action, parsed_id, _ = extract_button_action({
            "type": "interactive",
            "interactive": {
                "button_reply": {
                    "id": f"cancelar:{appointment_id}",
                    "title": "Cancelar Consulta",
                }
            },
        })

        self.assertEqual(action, "cancelar")
        self.assertEqual(parsed_id, appointment_id)

    def test_iter_messages_and_statuses(self) -> None:
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "metadata": {"phone_number_id": "123"},
                        "messages": [{
                            "id": "wamid.incoming",
                            "from": "5511999999999",
                            "type": "button",
                        }],
                        "statuses": [{
                            "id": "wamid.outgoing",
                            "status": "delivered",
                            "timestamp": "123456",
                            "recipient_id": "5511999999999",
                        }],
                    }
                }]
            }]
        }

        events = iter_webhook_events(payload)

        self.assertEqual([event["kind"] for event in events], ["message", "status"])
        self.assertEqual(events[0]["event_id"], "wamid.incoming")
        self.assertEqual(events[1]["event_id"], "status:wamid.outgoing:delivered:123456")

    def test_verify_signature(self) -> None:
        body = b'{"object":"whatsapp_business_account"}'
        secret = "app-secret"
        digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        self.assertTrue(verify_whatsapp_signature(body, f"sha256={digest}", secret))
        self.assertFalse(verify_whatsapp_signature(body, "sha256=invalid", secret))
        self.assertTrue(verify_whatsapp_signature(body, None, ""))


if __name__ == "__main__":
    unittest.main()
