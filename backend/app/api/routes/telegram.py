from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.application.services.chat_service import ChatService
from app.infrastructure.channels.telegram_adapter import TelegramChannelAdapter

router = APIRouter(prefix="/telegram", tags=["telegram"])


class TelegramMessagePayload(BaseModel):
    """Schema para mensaje de Telegram"""

    chat_id: int
    user_id: int
    text: str
    role: str = "profesor"


@router.post("/messages")
def receive_telegram_message(
    payload: TelegramMessagePayload, request: Request
) -> dict:
    """
    Endpoint para recibir mensajes de Telegram.
    
    En producción, esto sería un webhook que Telegram envía.
    Por ahora permite testing manual.
    """
    chat_service: ChatService = request.app.state.chat_service
    telegram_adapter = TelegramChannelAdapter()

    try:
        # Normalizar el mensaje
        command = telegram_adapter.normalize_incoming(payload.model_dump())

        # Procesar con ChatService
        result = chat_service.send_message(command)

        return {
            "conversation_id": result.conversation_id,
            "role": result.role,
            "channel": result.channel,
            "user_message": {
                "id": result.user_message.id,
                "content": result.user_message.content,
                "created_at": result.user_message.created_at.isoformat(),
            },
            "assistant_message": {
                "id": result.assistant_message.id,
                "content": result.assistant_message.content,
                "created_at": result.assistant_message.created_at.isoformat(),
            },
            "model": result.model,
        }

    except Exception as exc:
        return {"error": str(exc), "details": str(type(exc).__name__)}


@router.get("/status")
def telegram_status() -> dict:
    """Health check para Telegram integration"""
    return {"status": "online", "service": "telegram-adapter"}
