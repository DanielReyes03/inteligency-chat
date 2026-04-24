from app.application.errors import NotFoundAppError, ValidationAppError
from app.application.ports.conversation_repository import ConversationRepository
from app.application.ports.llm_client import LLMClient
from app.application.ports.user_context_repository import UserContextRepository
from app.domain.models import ChatResult, IncomingChatCommand
from app.domain.roles import build_enriched_system_prompt, get_role_profile


class ChatService:
    def __init__(
        self,
        *,
        repository: ConversationRepository,
        llm_client: LLMClient,
        user_context_repository: UserContextRepository | None = None,
    ) -> None:
        self._repository = repository
        self._llm_client = llm_client
        self._user_context_repository = user_context_repository

    def send_message(self, command: IncomingChatCommand) -> ChatResult:
        role = command.role.strip().lower()
        role_profile = get_role_profile(role)
        if role_profile is None:
            raise ValidationAppError(
                code="INVALID_ROLE", message="El rol seleccionado no existe"
            )

        message = command.message.strip()
        if not message:
            raise ValidationAppError(
                code="EMPTY_MESSAGE", message="El mensaje no puede estar vacío"
            )

        conversation = self._repository.get_or_create(
            command.conversation_id,
            channel=command.channel,
            role=role,
            user_id=command.user_id,
        )

        if command.conversation_id is not None and conversation.role != role:
            raise ValidationAppError(
                code="ROLE_MISMATCH",
                message="La conversación ya existe con otro rol",
            )

        user_message = self._repository.add_user_message(conversation.id, message)

        # 🔍 OBTENER CONTEXTO DEL USUARIO (si existe)
        user_context = None
        if self._user_context_repository and command.user_id:
            user_context = self._user_context_repository.get(command.user_id)

        # 🎯 CONSTRUIR SYSTEM PROMPT ENRIQUECIDO
        system_prompt = build_enriched_system_prompt(role, user_context)

        assistant_text = self._llm_client.generate(
            system_prompt=system_prompt,
            user_message=message,
        )
        if not assistant_text.strip():
            raise NotFoundAppError(
                code="EMPTY_ASSISTANT_RESPONSE",
                message="El modelo devolvió una respuesta vacía",
            )

        assistant_message = self._repository.add_assistant_message(
            conversation.id,
            assistant_text.strip(),
        )

        return ChatResult(
            conversation_id=conversation.id,
            role=conversation.role,
            channel=conversation.channel,
            user_message=user_message,
            assistant_message=assistant_message,
            model=self._llm_client.model_name,
        )

    def list_messages(self, conversation_id: str):
        if not conversation_id.strip():
            raise ValidationAppError(
                code="INVALID_CONVERSATION_ID",
                message="conversation_id es obligatorio",
            )
        return self._repository.list_messages(conversation_id)
