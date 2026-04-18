# Chat inteligente con roles (MVP)

Bootstrap MVP con:

- **FastAPI** (API + hosting de estáticos)
- **SQLite** (persistencia de conversaciones y mensajes)
- **Ollama local** (generación de respuestas)
- **Frontend HTML/JS mínimo**
- **Contratos de adapters** para futuros canales

## Alcance MVP

Incluye:

- Catálogo de roles fijo: `profesor`, `programador`, `psicologo`, `negocios`
- Endpoint para enviar mensajes: `POST /api/v1/chat/messages`
- Endpoint para historial: `GET /api/v1/chat/conversations/{conversation_id}/messages`
- Endpoint de roles: `GET /api/v1/roles`
- UI mínima en `/`

No incluye (fuera de alcance en este cambio):

- Integración completa de `bot-whatsapp`
- Autenticación
- Panel admin
- Streaming de tokens
- RAG / vector DB

## Requisitos

- Python 3.11+
- Ollama corriendo localmente

## Setup local

```bash
cp backend/.env.example backend/.env
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Ejecutar app

```bash
uvicorn app.main:app --reload --app-dir backend
```

Abrí: `http://127.0.0.1:8000/`

## Ejecutar tests

```bash
pytest backend/tests
```

## Variables de entorno

Definidas en `backend/.env.example`:

- `DATABASE_URL` (default: `sqlite:///./chat_roles.db`)
- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `llama3.1`)
- `OLLAMA_TIMEOUT_SECONDS` (default: `30`)
