#!/bin/bash

# Script para iniciar todo el sistema: API + Bot Telegram

set -e

echo "🚀 Chat Inteligente - Iniciador de Sistema"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar si estamos en el directorio correcto
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Error: ejecuta este script desde la raíz del proyecto${NC}"
    exit 1
fi

# Verificar Token de Telegram
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN no está configurado${NC}"
    echo "Obtén el token de @BotFather en Telegram y ejecuta:"
    echo ""
    echo "  export TELEGRAM_BOT_TOKEN='tu_token_aqui'"
    echo "  bash start.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Token de Telegram detectado${NC}"
echo ""

# Cambiar a backend
cd backend

# Crear venv si no existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Activar venv
echo -e "${YELLOW}🔌 Activando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar dependencias
echo -e "${YELLOW}📚 Instalando dependencias...${NC}"
pip install -q -r requirements.txt

echo ""
echo -e "${GREEN}✅ Ambiente preparado${NC}"
echo ""
echo "Para comenzar, abre 3 terminales:"
echo ""
echo "Terminal 1 - Ollama:"
echo "  ollama serve"
echo ""
echo "Terminal 2 - API FastAPI:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 3 - Bot de Telegram:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  export TELEGRAM_BOT_TOKEN='$TELEGRAM_BOT_TOKEN'"
echo "  python telegram_bot.py"
echo ""
echo "Luego, en Telegram busca tu bot y escribe /start 🎉"
echo ""
