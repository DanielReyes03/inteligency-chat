# 🎉 Guía: Contexto Enriquecido + Telegram

## ✅ Lo que implementamos

1. **Contexto de Usuario**: BD para almacenar información enriquecida por rol
2. **Prompts Dinámicos**: System prompts que se adaptan al contexto del usuario
3. **Telegram Integration**: Canal Telegram para chat
4. **API de Contexto**: Endpoints para gestionar el contexto del usuario

---

## 🚀 Cómo funciona

### Flujo con Contexto

```
Usuario Telegram/Web
    ↓
Envía: {chat_id, user_id, text, role}
    ↓
TelegramAdapter normaliza
    ↓
ChatService obtiene UserContext (si existe)
    ↓
build_enriched_system_prompt() crea prompt personalizado
    ↓
Ollama recibe prompt + contexto
    ↓
Respuesta contextualizada
```

### Ejemplo: Profesor con contexto educativo

**Antes (sin contexto):**
```
system: "Sos un profesor paciente. Explicá conceptos..."
user: "¿Qué es una clase en Python?"
```

**Después (con contexto):**
```
system: "Sos un profesor paciente...
El estudiante está aprendiendo: Python, Django, SQL
Nivel: principiante
Tiene dificultades con: decoradores, async/await
Estilo preferido: con ejemplos
Objetivos: crear APIs REST"

user: "¿Qué es una clase en Python?"
```

El modelo adapta su respuesta considerando el nivel, dificultades, etc.

---

## 📝 Usar desde cURL

### 1️⃣ Crear/Actualizar contexto de usuario

```bash
# Contexto educativo (profesor)
curl -X POST "http://localhost:8000/api/v1/context/users/user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "educational_profile": {
      "materias": ["Python", "Django", "SQL"],
      "nivel": "principiante",
      "dificultades": ["decoradores", "async/await"],
      "estilo_enseñanza": "con ejemplos",
      "objetivos": ["crear APIs REST"]
    }
  }'
```

```bash
# Contexto técnico (programador)
curl -X POST "http://localhost:8000/api/v1/context/users/user-456" \
  -H "Content-Type: application/json" \
  -d '{
    "technical_profile": {
      "lenguajes": ["Python", "JavaScript", "Go"],
      "nivel": "senior",
      "proyectos": "microservicios con Kubernetes",
      "estilo_explicacion": "conciso con ejemplos"
    }
  }'
```

```bash
# Contexto empresarial (negocios)
curl -X POST "http://localhost:8000/api/v1/context/users/user-789" \
  -H "Content-Type: application/json" \
  -d '{
    "company_info": {
      "mision": "Democratizar la IA",
      "vision": "IA accesible para todos",
      "valores": "Transparencia, innovación",
      "productos": "Chat inteligente, análisis",
      "politicas": "Código abierto, privacidad",
      "horarios": "Lunes-viernes 9-18",
      "faqs": ["Cómo cambiar planes?", "Soporte 24/7?"]
    }
  }'
```

```bash
# Contexto psicológico (psicólogo)
curl -X POST "http://localhost:8000/api/v1/context/users/user-999" \
  -H "Content-Type: application/json" \
  -d '{
    "psychological_profile": {
      "sentimientos": "ansioso pero motivado",
      "situaciones_estresantes": ["presión laboral", "relaciones"],
      "objetivos_bienestar": ["reducir estrés", "mejorar sueño"],
      "preferencias_comunicacion": "empática, informal"
    }
  }'
```

### 2️⃣ Obtener contexto

```bash
curl http://localhost:8000/api/v1/context/users/user-123
```

Respuesta:
```json
{
  "user_id": "user-123",
  "educational_profile": {
    "materias": ["Python", "Django", "SQL"],
    "nivel": "principiante",
    ...
  },
  "created_at": "2024-04-23T...",
  "updated_at": "2024-04-23T..."
}
```

### 3️⃣ Enviar mensaje por Telegram (simulado)

```bash
curl -X POST "http://localhost:8000/api/v1/telegram/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456,
    "user_id": "user-123",
    "text": "¿Cómo funciona un decorador en Python?",
    "role": "profesor"
  }'
```

Respuesta:
```json
{
  "conversation_id": "123456",
  "role": "profesor",
  "channel": "telegram",
  "user_message": {
    "id": "...",
    "content": "¿Cómo funciona un decorador en Python?",
    "created_at": "..."
  },
  "assistant_message": {
    "id": "...",
    "content": "Un decorador es una función que modifica otra función...",
    "created_at": "..."
  },
  "model": "kimi-k2.5"
}
```

### 4️⃣ Chat normal (Web) - Ahora con contexto

```bash
curl -X POST "http://localhost:8000/api/v1/chat/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "channel": "web",
    "role": "programador",
    "user_id": "user-456",
    "message": "¿Cómo optimizar este código?"
  }'
```

El servicio:
1. Obtiene contexto técnico de user-456
2. Crea prompt: "Sos un programador senior... Lenguajes: Python, JavaScript, Go..."
3. Ollama responde considerando el contexto

---

## 🔧 Estructura de Contextos

### educational_profile
```python
{
  "materias": ["Python", "Django"],
  "nivel": "principiante|intermedio|avanzado",
  "dificultades": ["decoradores", "async"],
  "estilo_enseñanza": "visual|auditivo|kinestésico|con ejemplos",
  "objetivos": ["crear APIs", "entender OOP"]
}
```

### technical_profile
```python
{
  "lenguajes": ["Python", "JavaScript"],
  "nivel": "junior|mid|senior",
  "proyectos": "microservicios, APIs REST",
  "estilo_explicacion": "detallado|conciso|con ejemplos"
}
```

### psychological_profile
```python
{
  "sentimientos": "ansioso, motivado",
  "situaciones_estresantes": ["presión", "deadlines"],
  "objetivos_bienestar": ["reducir estrés"],
  "preferencias_comunicacion": "empática|formal|informal"
}
```

### company_info
```python
{
  "mision": "...",
  "vision": "...",
  "valores": "...",
  "productos": "...",
  "politicas": "...",
  "horarios": "...",
  "faqs": ["...", "..."]
}
```

---

## 📊 Arquitectura DB

Nueva tabla: `users_context`

```sql
users_context (
  user_id TEXT PRIMARY KEY,
  company_info JSON,           -- Para rol "negocios"
  educational_profile JSON,    -- Para rol "profesor"
  psychological_profile JSON,  -- Para rol "psicologo"
  technical_profile JSON,      -- Para rol "programador"
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

---

## 🤖 Cómo Telegram funcionará en Producción

### 1. Crear Bot en Telegram
```bash
# Habla con @BotFather en Telegram
# Obtén: TOKEN
```

### 2. Webhook Setup
```python
# En app/infrastructure/channels/telegram_webhook.py (crear)
from telegram import Update
from telegram.ext import Application

application = Application.builder().token(TELEGRAM_TOKEN).build()

# Registrar handlers
```

### 3. Endpoint Webhook
```python
@router.post("/webhook")  # Telegram enviará aquí
async def telegram_webhook(request: Request):
    # Recibe Update de Telegram
    # Llama a ChatService
    # Responde con mensaje
```

Por ahora, el endpoint `/api/v1/telegram/messages` permite testing manual.

---

## 🧪 Ejemplo Completo

### Escenario: Estudiante con contexto educativo

**Paso 1: Crear contexto**
```bash
curl -X POST "http://localhost:8000/api/v1/context/users/student-001" \
  -H "Content-Type: application/json" \
  -d '{
    "educational_profile": {
      "materias": ["Python", "Bases de Datos"],
      "nivel": "principiante",
      "dificultades": ["funciones", "listas"],
      "estilo_enseñanza": "con ejemplos",
      "objetivos": ["aprobar el curso"]
    }
  }'
```

**Paso 2: Enviar mensaje**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student-001",
    "role": "profesor",
    "message": "¿Cómo hago una lista en Python?"
  }'
```

**Respuesta del modelo:**
```
Un profesor senior verá:
- Estudiante principiante
- Tiene dificultades con: listas
- Estilo: con ejemplos

→ Explicará paso a paso con ejemplos concretos
```

---

## 📦 Dependencias Nuevas

```bash
pip install python-telegram-bot==21.5
```

---

## 🚦 Status de Implementación

- ✅ Modelos de datos (UserContext, EnrichedChatCommand)
- ✅ BD: tabla users_context
- ✅ Repositorio SQLite para contexto
- ✅ Adaptador Telegram
- ✅ Prompts dinámicos por rol + contexto
- ✅ ChatService enriquecido
- ✅ Rutas API: /context, /telegram
- ✅ Main.py actualizado
- ⏳ Webhook real de Telegram (en desarrollo)
- ⏳ Tests unitarios
- ⏳ Documentación Swagger mejorada

---

## 🔮 Próximos Pasos

1. **Webhook Telegram**: Conectar bot real
2. **Persistencia**: Guardar contexto entre sesiones
3. **Analytics**: Medir qué contextos funcionan mejor
4. **Multi-idioma**: Adaptar prompts por idioma
5. **Feedback**: Actualizar contexto basado en feedback del usuario
