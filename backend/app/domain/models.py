from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RoleProfile:
    id: str
    label: str
    description: str
    system_prompt: str


@dataclass(slots=True)
class Conversation:
    id: str
    channel: str
    role: str
    user_id: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class Message:
    id: str
    conversation_id: str
    sender: str
    content: str
    created_at: datetime


@dataclass(slots=True)
class IncomingChatCommand:
    conversation_id: str | None
    channel: str
    role: str
    user_id: str | None
    message: str


@dataclass(slots=True)
class ChatResult:
    conversation_id: str
    role: str
    channel: str
    user_message: Message
    assistant_message: Message
    model: str


@dataclass(slots=True)
class UserContext:
    """Contexto enriquecido del usuario por rol"""
    user_id: str
    
    # Contexto empresarial
    company_info: dict | None = None  # {misión, visión, valores, productos, horarios, faqs}
    
    # Contexto educativo
    educational_profile: dict | None = None  # {materias, nivel, dificultades, estilo_enseñanza, objetivos}
    
    # Contexto psicológico
    psychological_profile: dict | None = None  # {sentimientos, situaciones, objetivos, preferencias_comunicacion}
    
    # Contexto técnico
    technical_profile: dict | None = None  # {lenguajes, proyectos, nivel, estilo_explicacion}
    
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class EnrichedChatCommand(IncomingChatCommand):
    """Comando de chat enriquecido con contexto del usuario"""
    user_context: UserContext | None = None
