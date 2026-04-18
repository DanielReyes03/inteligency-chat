from fastapi import APIRouter

from app.api.schemas.chat import RoleResponse
from app.domain.roles import list_roles

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleResponse])
def get_roles() -> list[RoleResponse]:
    return [
        RoleResponse(id=role.id, label=role.label, description=role.description)
        for role in list_roles()
    ]
