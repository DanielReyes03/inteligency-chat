from fastapi import APIRouter, Request

from app.api.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationMessageResponse,
    HistoryResponse,
)
from app.application.services.chat_service import ChatService
from app.infrastructure.channels.web_adapter import WebChannelAdapter

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def _get_web_adapter(request: Request) -> WebChannelAdapter:
    return request.app.state.web_adapter


@router.post("/messages", response_model=ChatMessageResponse)
def post_message(payload: ChatMessageRequest, request: Request) -> ChatMessageResponse:
    chat_service = _get_chat_service(request)
    web_adapter = _get_web_adapter(request)
    command = web_adapter.normalize_incoming(payload.model_dump())
    result = chat_service.send_message(command)

    return ChatMessageResponse(
        conversation_id=result.conversation_id,
        role=result.role,
        channel=result.channel,
        user_message={
            "id": result.user_message.id,
            "content": result.user_message.content,
            "created_at": result.user_message.created_at,
        },
        assistant_message={
            "id": result.assistant_message.id,
            "content": result.assistant_message.content,
            "created_at": result.assistant_message.created_at,
        },
        model=result.model,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=HistoryResponse)
def get_history(conversation_id: str, request: Request) -> HistoryResponse:
    chat_service = _get_chat_service(request)
    history = chat_service.list_messages(conversation_id)
    return HistoryResponse(
        conversation_id=conversation_id,
        messages=[
            ConversationMessageResponse(
                id=message.id,
                sender=message.sender,
                content=message.content,
                created_at=message.created_at,
            )
            for message in history
        ],
    )
