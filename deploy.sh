#!/bin/bash
set -e  # para o script caso algum comando falhe

# ==============================
# CONFIGURAÇÕES
# ==============================
REGION="southamerica-east1"
BACKEND_SERVICE="telegram-forward-backend"
FRONTEND_SERVICE="telegram-forward-ui"
API_TOKEN="meu_token_super_seguro_123"

echo "🚀 Iniciando deploy automático..."

# ==========================
# AUTENTICAÇÃO GCLOUD
# ==========================
ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null || true)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "Nenhuma conta gcloud ativa. Realizando login..."
    gcloud auth login
else
    echo "Conta gcloud ativa: $ACTIVE_ACCOUNT"
fi
gcloud config set project "$PROJECT_ID"
gcloud auth configure-docker

# ==========================
# GARANTIR QUE APP ENGINE EXISTE
# ==========================
echo "Verificando App Engine..."
if ! gcloud app describe --project "$PROJECT_ID" >/dev/null 2>&1; then
    echo "App Engine não encontrado. Criando..."
    gcloud app create --region=$REGION
else
    echo "App Engine já existe."
fi

# ==============================
# 1️⃣ DEPLOY DO BACKEND
# ==============================
echo "📦 Deploy do backend no Cloud Run..."
gcloud run deploy $BACKEND_SERVICE \
  --source ./backend \
  --region $REGION \
  --set-env-vars API_TOKEN=$API_TOKEN \
  --allow-unauthenticated \
  --quiet

# Captura a URL pública do backend
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
  --region $REGION \
  --format 'value(status.url)')

echo "✅ Backend implantado em: $BACKEND_URL"

# ==============================
# 2️⃣ ATUALIZA .ENV DO FRONTEND
# ==============================
echo "📝 Atualizando .env do frontend..."
FRONTEND_ENV_PATH="./frontend/.env"

# Cria o arquivo .env se não existir
if [ ! -f "$FRONTEND_ENV_PATH" ]; then
  touch "$FRONTEND_ENV_PATH"
fi

# Remove linhas antigas e escreve variáveis novas
grep -v "NEXT_PUBLIC_API_URL" "$FRONTEND_ENV_PATH" > "$FRONTEND_ENV_PATH.tmp" || true
grep -v "NEXT_PUBLIC_API_TOKEN" "$FRONTEND_ENV_PATH.tmp" > "$FRONTEND_ENV_PATH.tmp2" || true
mv "$FRONTEND_ENV_PATH.tmp2" "$FRONTEND_ENV_PATH"

echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" >> "$FRONTEND_ENV_PATH"
echo "NEXT_PUBLIC_API_TOKEN=$API_TOKEN" >> "$FRONTEND_ENV_PATH"

echo "✅ .env do frontend atualizado:"
cat "$FRONTEND_ENV_PATH"

# ==============================
# 3️⃣ DEPLOY DO FRONTEND
# ==============================
echo "📦 Deploy do frontend no Cloud Run..."
gcloud run deploy $FRONTEND_SERVICE \
  --source ./frontend \
  --region $REGION \
  --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL,NEXT_PUBLIC_API_TOKEN=$API_TOKEN \
  --allow-unauthenticated \
  --quiet

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
  --region $REGION \
  --format 'value(status.url)')

echo "✅ Frontend implantado em: $FRONTEND_URL"

# ==============================
# ✅ FINALIZAÇÃO
# ==============================
echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "🌐 Backend:  $BACKEND_URL"
echo "💻 Frontend: $FRONTEND_URL"
