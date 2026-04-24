from app.domain.models import RoleProfile, UserContext


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


def build_enriched_system_prompt(
    role_id: str, user_context: UserContext | None = None
) -> str:
    """
    Construye un system_prompt enriquecido con contexto del usuario.
    Si no hay contexto, devuelve el prompt base del rol.
    """
    role = get_role_profile(role_id)
    if not role:
        return ""

    base_prompt = role.system_prompt

    if not user_context:
        return base_prompt

    # Agregar contexto según el rol
    if role_id == "profesor":
        return _enrich_profesor(base_prompt, user_context)
    elif role_id == "programador":
        return _enrich_programador(base_prompt, user_context)
    elif role_id == "psicologo":
        return _enrich_psicologo(base_prompt, user_context)
    elif role_id == "negocios":
        return _enrich_negocios(base_prompt, user_context)

    return base_prompt


def _enrich_profesor(base_prompt: str, user_context: UserContext) -> str:
    """Enriquece el prompt del profesor con contexto educativo"""
    context_parts = [base_prompt]

    if user_context.educational_profile:
        edu = user_context.educational_profile
        if edu.get("materias"):
            materias = ", ".join(edu["materias"])
            context_parts.append(f"\nEl estudiante está aprendiendo: {materias}")

        if edu.get("nivel"):
            context_parts.append(f"Nivel: {edu['nivel']}")

        if edu.get("dificultades"):
            dificultades = ", ".join(edu["dificultades"])
            context_parts.append(f"Tiene dificultades con: {dificultades}")

        if edu.get("estilo_enseñanza"):
            context_parts.append(f"Estilo preferido: {edu['estilo_enseñanza']}")

        if edu.get("objetivos"):
            objetivos = ", ".join(edu["objetivos"])
            context_parts.append(f"Objetivos: {objetivos}")

    return "\n".join(context_parts)


def _enrich_programador(base_prompt: str, user_context: UserContext) -> str:
    """Enriquece el prompt del programador con contexto técnico"""
    context_parts = [base_prompt]

    if user_context.technical_profile:
        tech = user_context.technical_profile
        if tech.get("lenguajes"):
            lenguajes = ", ".join(tech["lenguajes"])
            context_parts.append(f"\nLenguajes: {lenguajes}")

        if tech.get("nivel"):
            context_parts.append(f"Nivel de experiencia: {tech['nivel']}")

        if tech.get("proyectos"):
            context_parts.append(f"Proyectos actuales: {tech['proyectos']}")

        if tech.get("estilo_explicacion"):
            context_parts.append(f"Estilo: {tech['estilo_explicacion']}")

    return "\n".join(context_parts)


def _enrich_psicologo(base_prompt: str, user_context: UserContext) -> str:
    """Enriquece el prompt del psicólogo con contexto psicológico"""
    context_parts = [base_prompt]

    if user_context.psychological_profile:
        psych = user_context.psychological_profile
        if psych.get("sentimientos"):
            context_parts.append(f"\nEstado emocional actual: {psych['sentimientos']}")

        if psych.get("situaciones_estresantes"):
            situaciones = ", ".join(psych["situaciones_estresantes"])
            context_parts.append(f"Situaciones preocupantes: {situaciones}")

        if psych.get("objetivos_bienestar"):
            objetivos = ", ".join(psych["objetivos_bienestar"])
            context_parts.append(f"Objetivos de bienestar: {objetivos}")

        if psych.get("preferencias_comunicacion"):
            context_parts.append(
                f"Preferencias: {psych['preferencias_comunicacion']}"
            )

    return "\n".join(context_parts)


def _enrich_negocios(base_prompt: str, user_context: UserContext) -> str:
    """Enriquece el prompt del asesor de negocios con contexto empresarial"""
    context_parts = [base_prompt]

    if user_context.company_info:
        company = user_context.company_info
        if company.get("mision"):
            context_parts.append(f"\nMisión: {company['mision']}")

        if company.get("vision"):
            context_parts.append(f"Visión: {company['vision']}")

        if company.get("valores"):
            context_parts.append(f"Valores: {company['valores']}")

        if company.get("productos"):
            context_parts.append(f"Productos/Servicios: {company['productos']}")

        if company.get("politicas"):
            context_parts.append(f"Políticas clave: {company['politicas']}")

        if company.get("horarios"):
            context_parts.append(f"Horarios: {company['horarios']}")

        if company.get("faqs"):
            context_parts.append(f"FAQs comunes: {company['faqs']}")

    return "\n".join(context_parts)
