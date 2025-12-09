#!/bin/bash
# Script para iniciar a aplicação

export PYTHONPATH=/workspaces/CreditAI

echo "🚀 Iniciando CreditAI API..."
echo ""
echo "⚠️  AVISO: PostgreSQL e Redis devem estar rodando!"
echo "   Para iniciar todos os serviços, use: Dev Containers: Rebuild Container"
echo ""

cd /workspaces/CreditAI
python3 src/main.py
