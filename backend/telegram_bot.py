"""
Bot de Telegram que se conecta con la API FastAPI.

Variables de entorno requeridas (en backend/.env):
- TELEGRAM_BOT_TOKEN: Token del bot (@BotFather)
- FASTAPI_BASE_URL: URL de la API (default: http://localhost:8000)
"""

import logging
import os
import sys
from pathlib import Path

import httpx
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from telegram.constants import ChatAction

# Cargar .env desde la carpeta donde está este archivo (backend/)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Estados para conversación
SELECT_ROLE, CHATTING, UPDATING_CONTEXT = range(3)

# Roles disponibles
ROLES = {
    "🧑‍🏫 Profesor": "profesor",
    "💻 Programador": "programador",
    "🧠 Psicólogo": "psicologo",
    "💼 Negocios": "negocios",
}

# Preguntas de contexto por rol: (pregunta, clave_campo, es_lista)
CONTEXT_QUESTIONS = {
    "profesor": [
        ("¿Qué materias o temas estás estudiando? (separados por coma)", "materias", True),
        ("¿Cuál es tu nivel? (Principiante / Intermedio / Avanzado)", "nivel", False),
        ("¿Con qué temas tenés dificultades? (separados por coma, o 'ninguna')", "dificultades", True),
        ("¿Cómo preferís aprender? (ej: con ejemplos, paso a paso, visual)", "estilo_enseñanza", False),
    ],
    "programador": [
        ("¿Qué lenguajes de programación usás? (separados por coma)", "lenguajes", True),
        ("¿Cuál es tu nivel? (Principiante / Intermedio / Avanzado)", "nivel", False),
        ("¿En qué proyectos estás trabajando? (describí brevemente)", "proyectos", False),
        ("¿Cómo preferís las explicaciones? (detallado / conciso / con ejemplos)", "estilo_explicacion", False),
    ],
    "psicologo": [
        ("¿Cómo te sentís actualmente? (describí con libertad)", "sentimientos", False),
        ("¿Hay situaciones que te preocupan o estresan? (separadas por coma)", "situaciones_estresantes", True),
        ("¿Qué objetivos de bienestar tenés? (separados por coma)", "objetivos_bienestar", True),
        ("¿Cómo preferís comunicarte? (formal / informal / empático)", "preferencias_comunicacion", False),
    ],
    "negocios": [
        ("¿Cuál es la misión de tu empresa?", "mision", False),
        ("¿Cuál es la visión de tu empresa?", "vision", False),
        ("¿Qué productos o servicios ofrecen?", "productos", False),
        ("¿Cuáles son los valores de la empresa?", "valores", False),
    ],
}

ROLE_TO_PROFILE_KEY = {
    "profesor": "educational_profile",
    "programador": "technical_profile",
    "psicologo": "psychological_profile",
    "negocios": "company_info",
}

# Cliente HTTP
client = httpx.Client()
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000") + "/api/v1"


# ============================================================================
# COMANDOS
# ============================================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia el bot y pide seleccionar un rol"""
    user = update.effective_user
    welcome_text = (
        f"¡Hola {user.first_name}! 👋\n\n"
        "Bienvenido al Chat Inteligente.\n\n"
        "Selecciona un rol para comenzar:"
    )

    keyboard = [[rol] for rol in ROLES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    return SELECT_ROLE


async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el rol seleccionado y entra al chat"""
    user = update.effective_user
    user_choice = update.message.text

    if user_choice not in ROLES:
        await update.message.reply_text("Opción inválida. Intenta de nuevo.")
        return SELECT_ROLE

    # Guardar rol en contexto
    role_key = ROLES[user_choice]
    chat_id = str(update.message.chat_id)
    user_id = str(user.id)
    
    context.user_data["role"] = role_key
    context.user_data["user_id"] = user_id
    context.user_data["chat_id"] = chat_id
    context.user_data["conversation_id"] = None  # Se actualiza en el primer mensaje

    # Guardar contexto inicial del usuario (opcional)
    context.user_data["first_name"] = user.first_name
    context.user_data["last_name"] = user.last_name or ""
    
    # Crear contexto de usuario en la BD (para que esté inicializado)
    try:
        client.post(
            f"{FASTAPI_BASE_URL}/context/users/{user_id}",
            json={},
            timeout=5.0,
        )
    except Exception as exc:
        logger.warning(f"No se pudo crear contexto para {user_id}: {exc}")

    role_label = {v: k for k, v in ROLES.items()}[role_key]
    intro_text = (
        f"✅ Rol seleccionado: {role_label}\n\n"
        "Ahora puedes enviarme preguntas. "
        "Responderé como un experto en ese área.\n\n"
        "Comandos:\n"
        "/cambiar_rol - Cambiar a otro rol\n"
        "/contexto - Ver/actualizar tu contexto\n"
        "/historial - Ver historial de chat\n"
        "/cancelar - Cancelar conversación"
    )

    reply_markup = ReplyKeyboardRemove()
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

    return CHATTING


async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Procesa mensajes de chat"""
    user = update.effective_user
    message_text = update.message.text

    # Validar que tenga rol seleccionado
    if "role" not in context.user_data:
        await update.message.reply_text(
            "Primero debes seleccionar un rol. Usa /start"
        )
        return CHATTING

    # Mostrar "escribiendo..."
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        # Llamar a la API
        response = client.post(
            f"{FASTAPI_BASE_URL}/chat/messages",
            json={
                "conversation_id": context.user_data.get("conversation_id"),
                "chat_id": context.user_data.get("chat_id"),
                "channel": "telegram",
                "role": context.user_data["role"],
                "user_id": context.user_data["user_id"],
                "message": message_text,
            },
            timeout=60.0,  # Ollama puede ser lento
        )

        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Error desconocido")
            await update.message.reply_text(f"❌ Error: {error_msg}")
            return CHATTING

        # Procesar respuesta
        data = response.json()
        context.user_data["conversation_id"] = data["conversation_id"]

        assistant_response = data["assistant_message"]["content"]
        model = data["model"]

        # Dividir en partes si es muy largo (Telegram max 4096 caracteres)
        if len(assistant_response) > 4096:
            parts = [
                assistant_response[i : i + 4000]
                for i in range(0, len(assistant_response), 4000)
            ]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(assistant_response)

        # Mostrar metadata
        metadata = f"🤖 Modelo: {model} | 💬 ID: {data['conversation_id'][:8]}..."
        await update.message.reply_text(metadata, disable_notification=True)

    except httpx.TimeoutException:
        await update.message.reply_text(
            "⏱️ Timeout: El modelo tardó demasiado. Intenta de nuevo."
        )
    except Exception as exc:
        logger.exception("Error procesando mensaje", exc_info=exc)
        await update.message.reply_text(
            f"❌ Error interno: {str(exc)}\n\n"
            "Contacta al administrador si persiste."
        )

    return CHATTING


async def cambiar_rol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Permite cambiar de rol"""
    keyboard = [[rol] for rol in ROLES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Selecciona un nuevo rol:", reply_markup=reply_markup
    )

    return SELECT_ROLE


async def iniciar_actualizar_contexto(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Inicia el flujo para actualizar el contexto del usuario"""
    role = context.user_data.get("role", "profesor")
    questions = CONTEXT_QUESTIONS.get(role, [])

    if not questions:
        await update.message.reply_text("No hay preguntas de contexto para este rol.")
        return CHATTING

    context.user_data["context_questions"] = questions
    context.user_data["context_current_q"] = 0
    context.user_data["context_answers"] = {}

    role_label = {v: k for k, v in ROLES.items()}.get(role, role)
    await update.message.reply_text(
        f"Vamos a personalizar tu experiencia con {role_label}.\n"
        f"Son {len(questions)} preguntas cortas. Podés escribir 'omitir' para saltear cualquiera.\n\n"
        f"Pregunta 1/{len(questions)}:\n{questions[0][0]}"
    )
    return UPDATING_CONTEXT


async def recolectar_contexto(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recolecta respuestas de contexto una por una"""
    questions = context.user_data.get("context_questions", [])
    current_idx = context.user_data.get("context_current_q", 0)
    answers = context.user_data.get("context_answers", {})

    answer = update.message.text.strip()
    _, field_key, is_list = questions[current_idx]

    if answer.lower() != "omitir":
        if is_list:
            answers[field_key] = [item.strip() for item in answer.split(",") if item.strip()]
        else:
            answers[field_key] = answer
        context.user_data["context_answers"] = answers

    next_idx = current_idx + 1
    context.user_data["context_current_q"] = next_idx

    if next_idx < len(questions):
        await update.message.reply_text(
            f"Pregunta {next_idx + 1}/{len(questions)}:\n{questions[next_idx][0]}\n\n"
            f"(o escribí 'omitir' para saltear)"
        )
        return UPDATING_CONTEXT

    # Todas las preguntas respondidas → guardar
    role = context.user_data.get("role", "profesor")
    profile_key = ROLE_TO_PROFILE_KEY.get(role)
    user_id = context.user_data.get("user_id")

    try:
        client.post(
            f"{FASTAPI_BASE_URL}/context/users/{user_id}",
            json={profile_key: answers},
            timeout=10.0,
        )
        await update.message.reply_text(
            "✅ Contexto guardado. Mis respuestas ahora estarán personalizadas para vos.\n\n"
            "Podés seguir chateando normalmente."
        )
    except Exception as exc:
        logger.error("Error guardando contexto", exc_info=exc)
        await update.message.reply_text("❌ Error al guardar el contexto. Intenta de nuevo.")

    return CHATTING


async def mostrar_contexto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el contexto actual del usuario"""
    user_id = str(update.effective_user.id)

    try:
        response = client.get(f"{FASTAPI_BASE_URL}/context/users/{user_id}")
        data = response.json()

        if response.status_code != 200 or "error" in data:
            await update.message.reply_text(
                "No tenés contexto guardado aún.\n"
                "Usá /actualizar_contexto para personalizarlo."
            )
            return

        def _fmt(val) -> str:
            if not val:
                return "Vacío"
            if isinstance(val, dict):
                return "\n  ".join(f"{k}: {v}" for k, v in val.items())
            return str(val)

        contexto_text = (
            f"📋 Tu contexto actual:\n\n"
            f"🏢 Empresa:\n  {_fmt(data.get('company_info'))}\n\n"
            f"📚 Educativo:\n  {_fmt(data.get('educational_profile'))}\n\n"
            f"🧠 Psicológico:\n  {_fmt(data.get('psychological_profile'))}\n\n"
            f"💻 Técnico:\n  {_fmt(data.get('technical_profile'))}\n\n"
            f"Usá /actualizar_contexto para modificarlo."
        )

        await update.message.reply_text(contexto_text)

    except Exception as exc:
        logger.error("Error obteniendo contexto", exc_info=exc)
        await update.message.reply_text("❌ Error al obtener contexto.")


async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el historial de la conversación"""
    if "conversation_id" not in context.user_data or not context.user_data["conversation_id"]:
        await update.message.reply_text("📭 No tienes mensajes en esta sesión. Envía un mensaje primero.")
        return

    conversation_id = context.user_data["conversation_id"]

    try:
        response = client.get(
            f"{FASTAPI_BASE_URL}/chat/conversations/{conversation_id}/messages"
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ Error al obtener historial.")
            return

        data = response.json()
        messages = data.get("messages", [])

        if not messages:
            await update.message.reply_text("📭 Sin mensajes.")
            return

        # Construir historial
        historial_text = f"📜 Historial ({len(messages)} mensajes):\n\n"

        for msg in messages[-10:]:  # Últimos 10
            sender = "👤 Tú" if msg["sender"] == "user" else "🤖 Bot"
            content = msg["content"][:100]  # Primeros 100 caracteres
            historial_text += f"{sender}: {content}...\n"

        await update.message.reply_text(historial_text)

    except Exception as exc:
        logger.error("Error obteniendo historial", exc_info=exc)
        await update.message.reply_text("❌ Error al obtener historial.")


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversación"""
    await update.message.reply_text(
        "👋 Conversación cancelada.\n\nUsa /start para comenzar de nuevo."
    )
    context.user_data.clear()
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra ayuda"""
    help_text = """
🤖 Chat Inteligente - Comandos disponibles:

/start - Iniciar y seleccionar rol
/cambiar_rol - Cambiar a otro rol
/contexto - Ver tu contexto guardado
/historial - Ver últimos mensajes
/cancelar - Cancelar conversación
/help - Mostrar este mensaje

🎭 Roles disponibles:
🧑‍🏫 Profesor - Explica conceptos
💻 Programador - Ayuda técnica
🧠 Psicólogo - Escucha y apoyo
💼 Negocios - Estrategia empresarial

💡 Simplemente envía un mensaje para chatear.
    """

    await update.message.reply_text(help_text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador de errores global"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    """Inicia el bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print(
            "Error: TELEGRAM_BOT_TOKEN no está configurado.\n"
            "Agrega TELEGRAM_BOT_TOKEN=<tu_token> en backend/.env\n"
            "Obtén el token hablando con @BotFather en Telegram."
        )
        sys.exit(1)

    # Crear aplicación
    application = Application.builder().token(token).build()

    # Conversación handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_role)],
            CHATTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message),
                CommandHandler("cambiar_rol", cambiar_rol),
                CommandHandler("actualizar_contexto", iniciar_actualizar_contexto),
            ],
            UPDATING_CONTEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recolectar_contexto),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    # Registrar handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("contexto", mostrar_contexto))
    application.add_handler(CommandHandler("historial", historial))
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)

    # Iniciar bot
    logger.info("🤖 Bot iniciado. Esperando mensajes...")
    application.run_polling()


if __name__ == "__main__":
    main()
