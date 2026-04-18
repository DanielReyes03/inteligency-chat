from app.infrastructure.db.repositories.sqlite_conversation_repository import (
    SQLiteConversationRepository,
)
from app.infrastructure.db.session import (
    create_engine_for_url,
    create_session_factory,
    init_db,
)


def test_persists_and_reads_messages_in_order(tmp_path):
    db_file = tmp_path / "test_repo.db"
    engine = create_engine_for_url(f"sqlite:///{db_file}")
    init_db(engine)
    session_factory = create_session_factory(engine)
    repository = SQLiteConversationRepository(session_factory)

    conversation = repository.get_or_create(
        None,
        channel="web",
        role="programador",
        user_id=None,
    )
    repository.add_user_message(conversation.id, "hola")
    repository.add_assistant_message(conversation.id, "respuesta")

    messages = repository.list_messages(conversation.id)
    assert [m.sender for m in messages] == ["user", "assistant"]
    assert [m.content for m in messages] == ["hola", "respuesta"]
