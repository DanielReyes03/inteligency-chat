from fastapi.testclient import TestClient

from app.application.errors import LLMUnavailableError
from app.config import Settings
from app.main import create_app


class FakeLLM:
    model_name = "fake-ollama-model"

    def __init__(self, *, fail: bool = False):
        self.fail = fail

    def generate(self, *, system_prompt: str, user_message: str) -> str:
        if self.fail:
            raise LLMUnavailableError()
        return f"respuesta::{user_message}"


def _create_test_client(tmp_path, *, fail_llm: bool = False):
    db_file = tmp_path / "integration.db"
    settings = Settings(
        DATABASE_URL=f"sqlite:///{db_file}",
        OLLAMA_BASE_URL="http://localhost:11434",
        OLLAMA_MODEL="llama3.1",
        OLLAMA_TIMEOUT_SECONDS=3,
    )
    app = create_app(settings=settings, llm_client=FakeLLM(fail=fail_llm))
    return TestClient(app)


def test_roles_and_chat_happy_path(tmp_path):
    client = _create_test_client(tmp_path)

    roles = client.get("/api/v1/roles")
    assert roles.status_code == 200
    assert {role["id"] for role in roles.json()} == {
        "profesor",
        "programador",
        "psicologo",
        "negocios",
    }

    response = client.post(
        "/api/v1/chat/messages",
        json={
            "channel": "web",
            "role": "programador",
            "message": "Explicame FastAPI",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["assistant_message"]["content"] == "respuesta::Explicame FastAPI"

    history = client.get(
        f"/api/v1/chat/conversations/{data['conversation_id']}/messages"
    )
    assert history.status_code == 200
    assert [msg["sender"] for msg in history.json()["messages"]] == [
        "user",
        "assistant",
    ]


def test_rejects_invalid_role_and_empty_message(tmp_path):
    client = _create_test_client(tmp_path)

    invalid_role = client.post(
        "/api/v1/chat/messages",
        json={"channel": "web", "role": "otro", "message": "hola"},
    )
    assert invalid_role.status_code == 400
    assert invalid_role.json()["error"]["code"] == "INVALID_ROLE"

    empty_message = client.post(
        "/api/v1/chat/messages",
        json={"channel": "web", "role": "programador", "message": "   "},
    )
    assert empty_message.status_code == 400
    assert empty_message.json()["error"]["code"] == "EMPTY_MESSAGE"


def test_returns_503_when_ollama_unavailable(tmp_path):
    client = _create_test_client(tmp_path, fail_llm=True)

    response = client.post(
        "/api/v1/chat/messages",
        json={"channel": "web", "role": "programador", "message": "hola"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "OLLAMA_UNAVAILABLE"
