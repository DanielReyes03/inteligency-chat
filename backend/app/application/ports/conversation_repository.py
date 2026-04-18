from typing import Protocol

from app.domain.models import Conversation, Message


class ConversationRepository(Protocol):
    def get_or_create(
        self,
        conversation_id: str | None,
        *,
        channel: str,
        role: str,
        user_id: str | None,
    ) -> Conversation: ...

    def add_user_message(self, conversation_id: str, content: str) -> Message: ...

    def add_assistant_message(self, conversation_id: str, content: str) -> Message: ...

    def list_messages(self, conversation_id: str) -> list[Message]: ...
