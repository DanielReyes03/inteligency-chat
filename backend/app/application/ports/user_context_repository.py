from abc import ABC, abstractmethod

from app.domain.models import UserContext


class UserContextRepository(ABC):
    """Puerto: Abstracción de almacenamiento de contexto de usuario"""

    @abstractmethod
    def get_or_create(self, user_id: str) -> UserContext:
        """Obtiene o crea contexto vacío para un usuario"""
        pass

    @abstractmethod
    def update(self, user_context: UserContext) -> UserContext:
        """Actualiza contexto del usuario"""
        pass

    @abstractmethod
    def get(self, user_id: str) -> UserContext | None:
        """Obtiene contexto del usuario, None si no existe"""
        pass
