from app.application.errors import ValidationAppError
from app.domain.models import IncomingChatCommand


class WebChannelAdapter:
    def normalize_incoming(self, payload: object) -> IncomingChatCommand:
        if not isinstance(payload, dict):
            raise ValidationAppError(
                code="INVALID_PAYLOAD", message="Payload inválido para canal web"
            )

        channel = str(payload.get("channel", "web") or "web").strip().lower()
        if channel != "web":
            raise ValidationAppError(
                code="INVALID_CHANNEL",
                message="Solo se soporta el canal web en este MVP",
            )

        role = str(payload.get("role", "")).strip().lower()
        message = str(payload.get("message", ""))
        conversation_id = payload.get("conversation_id")
        user_id = payload.get("user_id")

        return IncomingChatCommand(
            conversation_id=str(conversation_id).strip() if conversation_id else None,
            channel=channel,
            role=role,
            user_id=str(user_id).strip() if user_id else None,
            message=message,
        )
