from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import (
    appointments,
    auth,
    billing,
    dashboard,
    email_test,
    patients,
    push,
    whatsapp_templates,
    whatsapp_test,
    whatsapp_webhook,
)

api_router = APIRouter()


@api_router.get("/health")
def health() -> dict:
    return {"ok": True}

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(billing.router, tags=["billing"])
api_router.include_router(push.router)
api_router.include_router(email_test.router)
api_router.include_router(whatsapp_test.router)
api_router.include_router(whatsapp_templates.router)
api_router.include_router(whatsapp_webhook.router)
