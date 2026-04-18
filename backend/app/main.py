import logging
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.roles import router as roles_router
from app.application.errors import AppError
from app.application.services.chat_service import ChatService
from app.config import Settings, get_settings
from app.infrastructure.channels.web_adapter import WebChannelAdapter
from app.infrastructure.db.repositories.sqlite_conversation_repository import (
    SQLiteConversationRepository,
)
from app.infrastructure.db.session import (
    create_engine_for_url,
    create_session_factory,
    init_db,
)
from app.infrastructure.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


def _error_envelope(*, code: str, message: str, details: object = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


def create_app(
    *,
    settings: Settings | None = None,
    repository: SQLiteConversationRepository | None = None,
    llm_client: OllamaClient | None = None,
) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(title="Chat Inteligente con Roles", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = create_engine_for_url(app_settings.DATABASE_URL)
    session_factory = create_session_factory(engine)
    init_db(engine)

    chat_repository = repository or SQLiteConversationRepository(session_factory)
    model_client = llm_client or OllamaClient(
        base_url=app_settings.OLLAMA_BASE_URL,
        model_name=app_settings.OLLAMA_MODEL,
        timeout_seconds=app_settings.OLLAMA_TIMEOUT_SECONDS,
    )

    app.state.chat_service = ChatService(
        repository=chat_repository,
        llm_client=model_client,
    )
    app.state.web_adapter = WebChannelAdapter()

    @app.exception_handler(AppError)
    async def _app_error_handler(_, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(
                code=exc.code, message=exc.message, details=exc.details
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def _request_validation_handler(_, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content=_error_envelope(
                code="REQUEST_VALIDATION_ERROR",
                message="La request no cumple el contrato esperado",
                details=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def _fallback_handler(_, exc: Exception):
        logger.exception("Unexpected error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=_error_envelope(
                code="INTERNAL_SERVER_ERROR",
                message="Ocurrió un error interno inesperado",
            ),
        )

    router = APIRouter(prefix="/api/v1")
    router.include_router(health_router)
    router.include_router(roles_router)
    router.include_router(chat_router)
    app.include_router(router)

    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()
