from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/context", tags=["context"])


class UserContextSchema(BaseModel):
    """Schema para actualizar contexto del usuario"""

    company_info: dict | None = None
    educational_profile: dict | None = None
    psychological_profile: dict | None = None
    technical_profile: dict | None = None


@router.post("/users/{user_id}")
def update_user_context(
    user_id: str, payload: UserContextSchema, request: Request
) -> dict:
    """Actualiza el contexto de un usuario"""
    user_context_repo = request.app.state.user_context_repository
    
    # Obtener o crear contexto
    user_context = user_context_repo.get_or_create(user_id)
    
    # Actualizar campos proporcionados
    if payload.company_info is not None:
        user_context.company_info = payload.company_info
    if payload.educational_profile is not None:
        user_context.educational_profile = payload.educational_profile
    if payload.psychological_profile is not None:
        user_context.psychological_profile = payload.psychological_profile
    if payload.technical_profile is not None:
        user_context.technical_profile = payload.technical_profile
    
    # Guardar
    updated = user_context_repo.update(user_context)
    
    return {
        "user_id": updated.user_id,
        "company_info": updated.company_info,
        "educational_profile": updated.educational_profile,
        "psychological_profile": updated.psychological_profile,
        "technical_profile": updated.technical_profile,
        "updated_at": updated.updated_at.isoformat() if updated.updated_at else None,
    }


@router.get("/users/{user_id}")
def get_user_context(user_id: str, request: Request) -> dict:
    """Obtiene el contexto de un usuario"""
    user_context_repo = request.app.state.user_context_repository
    user_context = user_context_repo.get(user_id)
    
    if not user_context:
        return {"error": "Usuario no encontrado", "user_id": user_id}
    
    return {
        "user_id": user_context.user_id,
        "company_info": user_context.company_info,
        "educational_profile": user_context.educational_profile,
        "psychological_profile": user_context.psychological_profile,
        "technical_profile": user_context.technical_profile,
        "created_at": user_context.created_at.isoformat() if user_context.created_at else None,
        "updated_at": user_context.updated_at.isoformat() if user_context.updated_at else None,
    }
