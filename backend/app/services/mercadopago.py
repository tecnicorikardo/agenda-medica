from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class MercadoPagoError(RuntimeError):
    pass


def _request_json(method: str, url: str, access_token: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise MercadoPagoError(f"Mercado Pago retornou {exc.code}: {raw}") from exc

    return json.loads(raw) if raw else {}


def create_preference(access_token: str, payload: dict) -> dict:
    return _request_json("POST", "https://api.mercadopago.com/checkout/preferences", access_token, payload)


def get_payment(access_token: str, payment_id: str) -> dict:
    return _request_json("GET", f"https://api.mercadopago.com/v1/payments/{payment_id}", access_token)
