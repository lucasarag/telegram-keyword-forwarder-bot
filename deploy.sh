#!/bin/bash
set -e

# ==========================
# CONFIGURAÇÕES
# ==========================
REGION="southamerica-east1"
BACKEND_SERVICE="telegram-forward-backend"
FRONTEND_SERVICE="telegram-forward-ui"
API_TOKEN="meu_token_super_seguro_123"



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

# ==========================
# VERIFICAÇÃO DO PROJECT_ID
# ==========================
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Nenhum projeto Google Cloud configurado."
    echo "Listando projetos disponíveis..."
    gcloud projects list
    echo ""
    read -p "Digite o PROJECT_ID que deseja usar: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi
echo "✅ Projeto atual: $PROJECT_ID"

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

# ==========================
# DEPLOY BACKEND
# ==========================
echo "🚀 Iniciando deploy do backend..."
gcloud run deploy $BACKEND_SERVICE \
  --source ./backend \
  --region $REGION \
  --set-env-vars API_TOKEN=$API_TOKEN \
  --allow-unauthenticated \
  --quiet

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
  --region $REGION \
  --format 'value(status.url)')
echo "✅ Backend URL: $BACKEND_URL"

# ==========================
# ATUALIZA .ENV FRONTEND
# ==========================
FRONTEND_ENV_PATH="./frontend/.env"

grep -v "NEXT_PUBLIC_API_URL" "$FRONTEND_ENV_PATH" > "$FRONTEND_ENV_PATH.tmp" || true
grep -v "NEXT_PUBLIC_API_TOKEN" "$FRONTEND_ENV_PATH.tmp" > "$FRONTEND_ENV_PATH.tmp2" || true
mv "$FRONTEND_ENV_PATH.tmp2" "$FRONTEND_ENV_PATH"

echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" >> "$FRONTEND_ENV_PATH"
echo "NEXT_PUBLIC_API_TOKEN=$API_TOKEN" >> "$FRONTEND_ENV_PATH"
echo "✅ .env frontend atualizado"

# ==========================
# DEPLOY FRONTEND
# ==========================
echo "🚀 Iniciando deploy do frontend..."
gcloud run deploy $FRONTEND_SERVICE \
  --source ./frontend \
  --region $REGION \
  --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL,NEXT_PUBLIC_API_TOKEN=$API_TOKEN \
  --allow-unauthenticated \
  --quiet

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
  --region $REGION \
  --format 'value(status.url)')
echo "✅ Frontend URL: $FRONTEND_URL"

echo "🎉 Deploy concluído com sucesso!"
