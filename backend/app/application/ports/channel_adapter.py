from typing import Protocol

from app.domain.models import IncomingChatCommand


class ChannelAdapter(Protocol):
    def normalize_incoming(self, payload: object) -> IncomingChatCommand: ...
