# ---------------------------------------------------------
# ETAPA 1: Build do Frontend (React + Vite)
# ---------------------------------------------------------
FROM node:20-alpine AS frontend
WORKDIR /app

# Instala dependências
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --silent || true

# Copia o restante do frontend
COPY frontend ./

# Build do frontend
RUN npm run build


# ---------------------------------------------------------
# ETAPA 2: Backend (FastAPI + Telethon)
# ---------------------------------------------------------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do backend
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copia o backend
COPY backend backend

# Copia o frontend buildado para ser servido pelo FastAPI
COPY --from=frontend /app/dist frontend/dist

# Diretórios de dados (persistência de sessões e arquivos)
RUN mkdir -p /app/data/sessions

# Porta padrão FastAPI no Cloud Run
EXPOSE 8080

# Comando de inicialização
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
