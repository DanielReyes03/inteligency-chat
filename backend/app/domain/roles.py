from app.domain.models import RoleProfile


ROLE_CATALOG: dict[str, RoleProfile] = {
    "profesor": RoleProfile(
        id="profesor",
        label="Profesor",
        description="Explica con claridad, paso a paso y con ejemplos simples.",
        system_prompt=(
            "Sos un profesor paciente. Explicá conceptos con claridad, en pasos "
            "y con ejemplos concretos."
        ),
    ),
    "programador": RoleProfile(
        id="programador",
        label="Programador",
        description="Prioriza precisión técnica, buenas prácticas y ejemplos de código.",
        system_prompt=(
            "Sos un programador senior. Respondé con precisión técnica, buenas "
            "prácticas y ejemplos concretos cuando aporten valor."
        ),
    ),
    "psicologo": RoleProfile(
        id="psicologo",
        label="Psicólogo",
        description="Responde con empatía, escucha activa y lenguaje cuidadoso.",
        system_prompt=(
            "Sos un psicólogo orientado a escucha activa. Respondé con empatía, "
            "sin juicio, y con preguntas que ayuden a reflexionar."
        ),
    ),
    "negocios": RoleProfile(
        id="negocios",
        label="Negocios",
        description="Enfoca respuesta en estrategia, impacto y trade-offs.",
        system_prompt=(
            "Sos un asesor de negocios. Priorizá claridad estratégica, impacto y "
            "trade-offs accionables."
        ),
    ),
}


def get_role_profile(role_id: str) -> RoleProfile | None:
    return ROLE_CATALOG.get(role_id)


def list_roles() -> list[RoleProfile]:
    return list(ROLE_CATALOG.values())
