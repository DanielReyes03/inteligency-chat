# 🤖 Guía: Bot de Telegram

## 1️⃣ Crear el Bot en Telegram

### En tu teléfono o Desktop (Telegram):

1. Abre Telegram
2. Busca a **@BotFather** (es el bot oficial para crear bots)
3. Escribe `/newbot`
4. Sigue estos pasos:
   - **Nombre del bot**: "Chat Inteligente" (o lo que quieras)
   - **Username**: Algo único terminado en `bot`, ej: `chat_inteligente_v1_bot`

5. **BotFather te dará un TOKEN** (algo como):
   ```
   123456789:ABCdefGHIjklmnOPQRstuvWXYZ1234567890
   ```
   
   **GUARDA ESTE TOKEN** ⭐

---

## 2️⃣ Configurar Variables de Entorno

En la carpeta `backend/`, actualiza `.env.telegram`:

```bash
# backend/.env.telegram

TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnOPQRstuvWXYZ1234567890
FASTAPI_BASE_URL=http://localhost:8000/api/v1
LOG_LEVEL=INFO
```

O simplemente:
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklmnOPQRstuvWXYZ1234567890"
```

---

## 3️⃣ Instalar Dependencias

```bash
# Ya está en requirements.txt, pero asegurate:
pip install python-telegram-bot==21.5
```

---

## 4️⃣ Correr el Bot

```bash
# Terminal 1: API FastAPI
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Ollama
ollama serve

# Terminal 3: Bot de Telegram
cd backend
export TELEGRAM_BOT_TOKEN="TU_TOKEN_AQUI"
python telegram_bot.py
```

O todo en uno:

```bash
cd backend && TELEGRAM_BOT_TOKEN="TU_TOKEN" python telegram_bot.py
```

---

## 5️⃣ Usar el Bot

En Telegram:

1. Busca tu bot por username (ej: `@chat_inteligente_v1_bot`)
2. Escribe `/start`
3. Selecciona un rol:
   - 🧑‍🏫 Profesor
   - 💻 Programador
   - 🧠 Psicólogo
   - 💼 Negocios
4. **Escribe tu pregunta y el bot responde** 🚀

---

## 📝 Comandos del Bot

```
/start          - Iniciar y elegir rol
/cambiar_rol    - Cambiar a otro rol
/contexto       - Ver tu contexto guardado
/historial      - Ver últimos mensajes
/cancelar       - Salir
/help           - Ver todos los comandos
```

---

## 🎯 Ejemplo de Uso

```
Usuario: /start
Bot: ¡Hola José! Bienvenido. Selecciona un rol:
     [🧑‍🏫 Profesor]
     [💻 Programador]
     [🧠 Psicólogo]
     [💼 Negocios]

Usuario: [Toca "💻 Programador"]
Bot: ✅ Rol seleccionado: Programador
     Ahora puedes enviarme preguntas...

Usuario: ¿Cómo optimizar un bucle en Python?
Bot: 🤖 escribiendo...
     [respuesta detallada del modelo]
     🤖 Modelo: kimi-k2.5 | 💬 ID: abc123...

Usuario: /historial
Bot: 📜 Historial (2 mensajes):
     👤 Tú: ¿Cómo optimizar un bucle en Python?
     🤖 Bot: En Python hay varias formas...

Usuario: /cambiar_rol
Bot: Selecciona un nuevo rol:
     [🧑‍🏫 Profesor]
     ...
```

---

## 🔧 Cómo Funciona Internamente

```
Telegram
   ↓ (mensaje de usuario)
telegram_bot.py
   ↓ (extrae: chat_id, user_id, text, role)
FastAPI /chat/messages
   ↓ (procesa con ChatService)
Ollama
   ↓ (genera respuesta)
FastAPI (retorna JSON)
   ↓ (formatea respuesta)
telegram_bot.py
   ↓ (envía a Telegram)
Telegram
   ↓ (usuario ve respuesta)
```

---

## 🧪 Troubleshooting

### ❌ "TELEGRAM_BOT_TOKEN no está configurado"

```bash
# Solución:
export TELEGRAM_BOT_TOKEN="tu_token_aqui"
python telegram_bot.py
```

### ❌ "Connection refused" (no se conecta a FastAPI)

```bash
# Asegúrate que FastAPI está corriendo:
cd backend
uvicorn app.main:app --reload

# En otra terminal:
python telegram_bot.py
```

### ❌ "Timeout: El modelo tardó demasiado"

- Ollama está lento o colgado
- El modelo es muy grande para tu máquina
- Aumenta el timeout en `telegram_bot.py` (línea: `timeout=60.0`)

### ❌ "Error: The token is invalid"

- El token está mal copiado
- Está expirado (no debería, pero intenta crear uno nuevo)
- Caracteres especiales mal escapados

---

## 🚀 Mejoras Futuras

- ✅ Contexto del usuario (educational, technical, etc.)
- ⏳ Persistencia de conversaciones
- ⏳ Cambio de contexto en vivo
- ⏳ Integración con base de datos para estadísticas
- ⏳ Webhook en lugar de polling (más eficiente)
- ⏳ Soporte para imágenes y archivos
- ⏳ Integración con WhatsApp

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs:
   ```bash
   python telegram_bot.py 2>&1 | grep -i error
   ```

2. Verifica la API:
   ```bash
   curl http://localhost:8000/health
   ```

3. Prueba el endpoint de Telegram directamente:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/telegram/messages" \
     -H "Content-Type: application/json" \
     -d '{
       "chat_id": 123,
       "user_id": 456,
       "text": "test",
       "role": "profesor"
     }'
   ```

---

## 🎉 ¡Listo!

Ahora tienes un bot de Telegram completamente funcional que:
- ✅ Se conecta a tu API FastAPI
- ✅ Usa diferentes roles
- ✅ Persiste conversaciones
- ✅ Soporte para contexto de usuario
- ✅ Interfaz amigable

¡Disfruta chattando! 🚀
