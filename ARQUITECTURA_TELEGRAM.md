# 🎨 Arquitectura: Bot Telegram + API FastAPI

## Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                       📱 TELEGRAM USER                          │
│                   (José, María, Carlos...)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │ /start
                         │ Envía: "¿Cómo hago un bucle?"
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               🤖 TELEGRAM BOT (telegram_bot.py)                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Recibe mensaje de usuario                               ││
│  │ 2. Extrae: chat_id, user_id, text, role                   ││
│  │ 3. Valida que haya seleccionado rol                        ││
│  │ 4. Muestra "escribiendo..."                               ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────────┬────────────────────────────────────────┘
                         │ POST /chat/messages
                         │ {user_id, role, message, channel}
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              ⚡ FASTAPI (app/main.py)                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ POST /api/v1/chat/messages                                ││
│  │ TelegramChannelAdapter.normalize_incoming()               ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│            💼 ChatService (application/services)                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Valida rol y mensaje                                    ││
│  │ 2. get_or_create(conversation)                             ││
│  │ 3. Obtiene UserContext si existe                          ││
│  │ 4. build_enriched_system_prompt()                          ││
│  │ 5. Guarda user_message en BD                              ││
│  │ 6. Llama a Ollama                                          ││
│  │ 7. Guarda assistant_message en BD                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─┬────────────────────┬────────────────────┬─────────────────────┘
  │                    │                    │
  ↓                    ↓                    ↓
┌─────────────┐  ┌──────────────┐  ┌─────────────────────────────┐
│   SQLite    │  │  UserContext │  │   🧠 OLLAMA               │
│  Database   │  │  Repository  │  │  (kimi-k2.5, llama, etc)  │
└─────────────┘  └──────────────┘  └──────────┬──────────────────┘
                                              │ (genera respuesta)
                                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              ⚡ FASTAPI (retorna JSON)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ response JSON
                         │ {assistant_message, conversation_id}
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               🤖 TELEGRAM BOT (responde)                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Extrae respuesta del JSON                               ││
│  │ 2. Divide en partes si > 4096 caracteres                   ││
│  │ 3. Envía a Telegram                                         ││
│  │ 4. Muestra metadata (modelo, conversation_id)              ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────────┬────────────────────────────────────────┘
                         │ Envía mensaje
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   📱 TELEGRAM USER                              │
│              (recibe respuesta del modelo)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Terminales Necesarias

```bash
┌──────────────────────────────────────┐
│ Terminal 1: Ollama                   │
├──────────────────────────────────────┤
│ $ ollama serve                       │
│                                      │
│ Escucha en: localhost:11434          │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Terminal 2: FastAPI                  │
├──────────────────────────────────────┤
│ $ cd backend                         │
│ $ uvicorn app.main:app --reload ... │
│                                      │
│ Escucha en: localhost:8000           │
│ Swagger UI: localhost:8000/docs      │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Terminal 3: Bot Telegram             │
├──────────────────────────────────────┤
│ $ python telegram_bot.py             │
│                                      │
│ Se conecta a:                        │
│ - Telegram (api.telegram.org)        │
│ - FastAPI (localhost:8000)           │
│ - Espera mensajes                    │
└──────────────────────────────────────┘
```

---

## Componentes Clave

### 🤖 Bot Telegram (telegram_bot.py)

```python
# Estados de conversación
SELECT_ROLE   → Usuario elige rol
CHATTING      → Usuario envía mensajes

# Comandos
/start        → Iniciar bot
/cambiar_rol  → Cambiar rol
/contexto     → Ver contexto
/historial    → Ver mensajes previos
/cancelar     → Salir
```

### ⚡ FastAPI (app/main.py)

```python
POST /chat/messages          → Enviar mensaje
GET  /context/users/{id}     → Obtener contexto
POST /context/users/{id}     → Actualizar contexto
POST /telegram/messages      → Endpoint Telegram (para testing)
```

### 💾 Base de Datos (SQLite)

```sql
conversations    → Conversaciones (id, channel, role, user_id)
messages         → Mensajes (id, content, sender, created_at)
users_context    → Contexto de usuarios (educational, technical, etc)
```

### 🧠 Ollama (Local)

```
localhost:11434/api/generate

payload: {
  "model": "kimi-k2.5",
  "system": "Sos un profesor...",
  "prompt": "¿Qué es una clase?",
  "stream": false
}
```

---

## Variables de Ambiente

```bash
# Backend (.env)
DATABASE_URL=sqlite:///./chat_roles.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=kimi-k2.5
OLLAMA_TIMEOUT_SECONDS=30

# Bot Telegram (.env.telegram o export)
TELEGRAM_BOT_TOKEN=123456789:ABC...
FASTAPI_BASE_URL=http://localhost:8000/api/v1
LOG_LEVEL=INFO
```

---

## Flujo de Contexto

```
Usuario: "Soy estudiante de Python, nivel principiante"
         ↓
Bot: /start
     Selecciona rol: "Profesor"
     ↓
POST /context/users/user-123
{
  "educational_profile": {
    "materias": ["Python"],
    "nivel": "principiante",
    "dificultades": ["funciones", "listas"]
  }
}
     ↓
SQLite guarda en users_context
     ↓
Próximo mensaje:
     ↓
ChatService obtiene UserContext
     ↓
build_enriched_system_prompt() crea:
"Sos un profesor... El estudiante aprende Python, 
 nivel principiante, tiene dificultades con funciones..."
     ↓
Ollama recibe prompt enriquecido
     ↓
Respuesta personalizada 🎯
```

---

## Seguridad (Notas)

- 🔒 Token de Telegram: Nunca lo commits (usa .env)
- 🔒 FastAPI: CORS actualmente abierto (cambiar en producción)
- 🔒 BD: SQLite local (cambiar a PostgreSQL en producción)
- 🔒 Ollama: Sin autenticación (asegurar en producción)

---

## Troubleshooting

```bash
# Ver logs del bot
python telegram_bot.py 2>&1 | tail -f

# Verificar conexiones
curl http://localhost:8000/health           # FastAPI
curl http://localhost:11434/api/tags        # Ollama

# Test manual sin bot
curl -X POST "http://localhost:8000/api/v1/chat/messages" \
  -H "Content-Type: application/json" \
  -d '{"role":"profesor", "message":"Hola", "channel":"web"}'

# Ver base de datos
sqlite3 backend/chat_roles.db
> .tables
> SELECT * FROM conversations;
```

---

## Status

✅ Bot Telegram básico funcional
✅ Integración con API FastAPI
✅ Contexto de usuario enriquecido
✅ Múltiples roles
⏳ Webhook en lugar de polling
⏳ Autenticación usuario
⏳ Integración con WhatsApp
