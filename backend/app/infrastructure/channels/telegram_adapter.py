from app.application.errors import ValidationAppError
from app.domain.models import IncomingChatCommand


class TelegramChannelAdapter:
    """Adaptador para normalizar mensajes de Telegram"""

    def normalize_incoming(self, payload: object) -> IncomingChatCommand:
        """Convierte payload de Telegram a IncomingChatCommand"""
        if not isinstance(payload, dict):
            raise ValidationAppError(
                code="INVALID_PAYLOAD", message="Payload inválido para Telegram"
            )

        # Extraer campos del mensaje de Telegram
        # Puede venir como 'chat_id' o 'conversation_id'
        chat_id = payload.get("chat_id") or payload.get("conversation_id")
        if not chat_id:
            raise ValidationAppError(
                code="MISSING_CHAT_ID", 
                message="chat_id o conversation_id es obligatorio"
            )

        user_id = payload.get("user_id")
        if not user_id:
            raise ValidationAppError(
                code="MISSING_USER_ID", message="user_id es obligatorio"
            )

        # El mensaje puede venir como 'text' o 'message'
        message = str(payload.get("text") or payload.get("message", "")).strip()
        if not message:
            raise ValidationAppError(
                code="EMPTY_MESSAGE", message="El mensaje no puede estar vacío"
            )

        role = str(payload.get("role", "profesor")).strip().lower()
        conversation_id = str(chat_id)  # Usar chat_id como conversation_id

        return IncomingChatCommand(
            conversation_id=conversation_id,
            channel="telegram",
            role=role,
            user_id=str(user_id).strip(),
            message=message,
        )
