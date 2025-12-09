# Use uma imagem base do Python
FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye

# Definir diretório de trabalho
WORKDIR /workspaces/CreditAI

# Copiar arquivos de dependências para o contêiner
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Adicionar PYTHONPATH ao ambiente
ENV PYTHONPATH=/workspaces/CreditAI