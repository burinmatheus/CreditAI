#!/bin/bash
# Script de desenvolvimento com autoreload

export PYTHONPATH=/workspaces/CreditAI

echo "🚀 Iniciando CreditAI em modo desenvolvimento..."
echo "📁 Monitorando mudanças nos arquivos..."
echo "🔄 Autoreload habilitado"
echo ""

cd /workspaces/CreditAI

# Usar uvicorn com reload para desenvolvimento
uvicorn src.interfaces.http.flask_app:FastAPIApp.get_app() \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir src \
    --log-level info
