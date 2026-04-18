from datetime import datetime, timezone

import pytest

from app.application.errors import LLMUnavailableError, ValidationAppError
from app.application.services.chat_service import ChatService
from app.domain.models import Conversation, IncomingChatCommand, Message


class FakeRepository:
    def __init__(self):
        now = datetime.now(timezone.utc)
        self.conversation = Conversation(
            id="conv-1",
            channel="web",
            role="programador",
            user_id=None,
            created_at=now,
            updated_at=now,
        )
        self.messages: list[Message] = []

    def get_or_create(self, conversation_id, *, channel, role, user_id):
        if conversation_id is None:
            self.conversation.role = role
        return self.conversation

    def add_user_message(self, conversation_id, content):
        msg = Message(
            id="user-1",
            conversation_id=conversation_id,
            sender="user",
            content=content,
            created_at=datetime.now(timezone.utc),
        )
        self.messages.append(msg)
        return msg

    def add_assistant_message(self, conversation_id, content):
        msg = Message(
            id="assistant-1",
            conversation_id=conversation_id,
            sender="assistant",
            content=content,
            created_at=datetime.now(timezone.utc),
        )
        self.messages.append(msg)
        return msg

    def list_messages(self, conversation_id):
        return self.messages


class FakeLLM:
    model_name = "fake-model"

    def __init__(self):
        self.last_system_prompt = ""

    def generate(self, *, system_prompt: str, user_message: str) -> str:
        self.last_system_prompt = system_prompt
        return f"respuesta para: {user_message}"


def test_rejects_invalid_role():
    service = ChatService(repository=FakeRepository(), llm_client=FakeLLM())

    with pytest.raises(ValidationAppError) as exc:
        service.send_message(
            IncomingChatCommand(
                conversation_id=None,
                channel="web",
                role="rol-inexistente",
                user_id=None,
                message="hola",
            )
        )

    assert exc.value.code == "INVALID_ROLE"


def test_rejects_empty_message():
    service = ChatService(repository=FakeRepository(), llm_client=FakeLLM())

    with pytest.raises(ValidationAppError) as exc:
        service.send_message(
            IncomingChatCommand(
                conversation_id=None,
                channel="web",
                role="programador",
                user_id=None,
                message="   ",
            )
        )

    assert exc.value.code == "EMPTY_MESSAGE"


def test_uses_role_context_prompt():
    repo = FakeRepository()
    llm = FakeLLM()
    service = ChatService(repository=repo, llm_client=llm)

    result = service.send_message(
        IncomingChatCommand(
            conversation_id=None,
            channel="web",
            role="profesor",
            user_id=None,
            message="Qué es una API?",
        )
    )

    assert result.role == "profesor"
    assert "profesor" in llm.last_system_prompt.lower()


def test_propagates_ollama_failure():
    class FailingLLM:
        model_name = "fake-model"

        def generate(self, *, system_prompt: str, user_message: str) -> str:
            raise LLMUnavailableError()

    service = ChatService(repository=FakeRepository(), llm_client=FailingLLM())

    with pytest.raises(LLMUnavailableError):
        service.send_message(
            IncomingChatCommand(
                conversation_id=None,
                channel="web",
                role="programador",
                user_id=None,
                message="probando",
            )
        )
