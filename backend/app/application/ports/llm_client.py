from typing import Protocol


class LLMClient(Protocol):
    model_name: str

    def generate(self, *, system_prompt: str, user_message: str) -> str: ...
