from app.application.errors import ValidationAppError
from app.domain.models import IncomingChatCommand


class WhatsAppChannelAdapter:
    """Stub explícito: se implementará en un cambio posterior."""

    def normalize_incoming(self, payload: object) -> IncomingChatCommand:
        raise ValidationAppError(
            code="WHATSAPP_NOT_IMPLEMENTED",
            message="La integración completa de WhatsApp está fuera del alcance de este MVP",
            details={"scope": "mvp-bootstrap"},
        )
