import httpx
import pytest

from app.application.errors import LLMUnavailableError
from app.infrastructure.llm.ollama_client import OllamaClient


def test_sends_expected_payload_and_returns_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/generate"
        body = request.read().decode("utf-8")
        assert '"model":"llama3.1"' in body
        assert '"system":"system prompt"' in body
        assert '"prompt":"hola"' in body
        return httpx.Response(status_code=200, json={"response": "ok"})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    ollama = OllamaClient(
        base_url="http://localhost:11434",
        model_name="llama3.1",
        timeout_seconds=1,
        http_client=client,
    )

    output = ollama.generate(system_prompt="system prompt", user_message="hola")
    assert output == "ok"


def test_maps_http_failure_to_unavailable_error():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=503, json={"error": "down"})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    ollama = OllamaClient(
        base_url="http://localhost:11434",
        model_name="llama3.1",
        timeout_seconds=1,
        http_client=client,
    )

    with pytest.raises(LLMUnavailableError):
        ollama.generate(system_prompt="x", user_message="y")
