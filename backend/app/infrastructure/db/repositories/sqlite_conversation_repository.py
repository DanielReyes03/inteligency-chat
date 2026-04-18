from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.application.errors import NotFoundAppError
from app.domain.models import Conversation, Message
from app.infrastructure.db.models import ConversationORM, MessageORM


class SQLiteConversationRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _session(self):
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_or_create(
        self,
        conversation_id: str | None,
        *,
        channel: str,
        role: str,
        user_id: str | None,
    ) -> Conversation:
        with self._session() as session:
            if conversation_id:
                existing = session.get(ConversationORM, conversation_id)
                if existing is None:
                    raise NotFoundAppError(
                        code="CONVERSATION_NOT_FOUND",
                        message="La conversación solicitada no existe",
                    )
                return self._to_conversation(existing)

            new_conversation = ConversationORM(
                channel=channel, role=role, user_id=user_id
            )
            session.add(new_conversation)
            session.flush()
            session.refresh(new_conversation)
            return self._to_conversation(new_conversation)

    def add_user_message(self, conversation_id: str, content: str) -> Message:
        return self._add_message(
            conversation_id=conversation_id, sender="user", content=content
        )

    def add_assistant_message(self, conversation_id: str, content: str) -> Message:
        return self._add_message(
            conversation_id=conversation_id, sender="assistant", content=content
        )

    def _add_message(
        self, *, conversation_id: str, sender: str, content: str
    ) -> Message:
        with self._session() as session:
            conversation = session.get(ConversationORM, conversation_id)
            if conversation is None:
                raise NotFoundAppError(
                    code="CONVERSATION_NOT_FOUND",
                    message="No existe la conversación para guardar el mensaje",
                )

            message = MessageORM(
                conversation_id=conversation_id,
                sender=sender,
                content=content,
            )
            session.add(message)
            session.flush()

            conversation.updated_at = message.created_at
            session.flush()
            session.refresh(message)
            return self._to_message(message)

    def list_messages(self, conversation_id: str) -> list[Message]:
        with self._session() as session:
            conversation = session.get(ConversationORM, conversation_id)
            if conversation is None:
                raise NotFoundAppError(
                    code="CONVERSATION_NOT_FOUND",
                    message="La conversación solicitada no existe",
                )

            rows = session.scalars(
                select(MessageORM)
                .where(MessageORM.conversation_id == conversation_id)
                .order_by(MessageORM.created_at.asc())
            ).all()
            return [self._to_message(row) for row in rows]

    @staticmethod
    def _to_conversation(row: ConversationORM) -> Conversation:
        return Conversation(
            id=row.id,
            channel=row.channel,
            role=row.role,
            user_id=row.user_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_message(row: MessageORM) -> Message:
        return Message(
            id=row.id,
            conversation_id=row.conversation_id,
            sender=row.sender,
            content=row.content,
            created_at=row.created_at,
        )
