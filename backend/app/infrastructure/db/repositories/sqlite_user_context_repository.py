from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.application.ports.user_context_repository import UserContextRepository
from app.domain.models import UserContext
from app.infrastructure.db.models import UserContextORM


class SQLiteUserContextRepository(UserContextRepository):
    """Implementación SQLite de UserContextRepository"""

    def __init__(self, *, session: Session) -> None:
        self._session = session

    def get_or_create(self, user_id: str) -> UserContext:
        """Obtiene o crea contexto vacío para un usuario"""
        orm = self._session.query(UserContextORM).filter_by(user_id=user_id).first()

        if orm:
            return self._orm_to_domain(orm)

        # Crear nuevo contexto vacío
        now = datetime.now(timezone.utc)
        new_orm = UserContextORM(
            user_id=user_id,
            company_info=None,
            educational_profile=None,
            psychological_profile=None,
            technical_profile=None,
            created_at=now,
            updated_at=now,
        )
        self._session.add(new_orm)
        self._session.commit()

        return self._orm_to_domain(new_orm)

    def get(self, user_id: str) -> UserContext | None:
        """Obtiene contexto del usuario, None si no existe"""
        orm = self._session.query(UserContextORM).filter_by(user_id=user_id).first()
        return self._orm_to_domain(orm) if orm else None

    def update(self, user_context: UserContext) -> UserContext:
        """Actualiza contexto del usuario"""
        orm = self._session.query(UserContextORM).filter_by(
            user_id=user_context.user_id
        ).first()

        if not orm:
            # Crear nuevo si no existe
            now = datetime.now(timezone.utc)
            orm = UserContextORM(user_id=user_context.user_id, created_at=now)
            self._session.add(orm)

        orm.company_info = user_context.company_info
        orm.educational_profile = user_context.educational_profile
        orm.psychological_profile = user_context.psychological_profile
        orm.technical_profile = user_context.technical_profile
        orm.updated_at = datetime.now(timezone.utc)

        self._session.commit()
        return self._orm_to_domain(orm)

    @staticmethod
    def _orm_to_domain(orm: UserContextORM) -> UserContext:
        """Convierte ORM a modelo de dominio"""
        return UserContext(
            user_id=orm.user_id,
            company_info=orm.company_info,
            educational_profile=orm.educational_profile,
            psychological_profile=orm.psychological_profile,
            technical_profile=orm.technical_profile,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
