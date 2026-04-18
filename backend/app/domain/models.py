from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RoleProfile:
    id: str
    label: str
    description: str
    system_prompt: str


@dataclass(slots=True)
class Conversation:
    id: str
    channel: str
    role: str
    user_id: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class Message:
    id: str
    conversation_id: str
    sender: str
    content: str
    created_at: datetime


@dataclass(slots=True)
class IncomingChatCommand:
    conversation_id: str | None
    channel: str
    role: str
    user_id: str | None
    message: str


@dataclass(slots=True)
class ChatResult:
    conversation_id: str
    role: str
    channel: str
    user_message: Message
    assistant_message: Message
    model: str
