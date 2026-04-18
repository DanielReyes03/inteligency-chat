from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: object | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class ChatMessageRequest(BaseModel):
    conversation_id: str | None = None
    channel: str = "web"
    role: str
    user_id: str | None = None
    message: str


class MessagePayload(BaseModel):
    id: str
    content: str
    created_at: datetime


class ChatMessageResponse(BaseModel):
    conversation_id: str
    role: str
    channel: str
    user_message: MessagePayload
    assistant_message: MessagePayload
    model: str


class RoleResponse(BaseModel):
    id: str
    label: str
    description: str


class ConversationMessageResponse(BaseModel):
    id: str
    sender: str = Field(pattern="^(user|assistant)$")
    content: str
    created_at: datetime


class HistoryResponse(BaseModel):
    conversation_id: str
    messages: list[ConversationMessageResponse]


class HealthResponse(BaseModel):
    status: str = "ok"
    model_config = ConfigDict(extra="forbid")
