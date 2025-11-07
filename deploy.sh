#!/bin/bash
set -e

PROJECT_ID="telegram-keyword-forwarder"
REGION="southamerica-east1"
BACKEND_DIR="./backend"
FRONTEND_DIR="./frontend"
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
echo "Deploy do backend..."
BACKEND_URL=$(gcloud run deploy telegram-forward-backend \
    --source $BACKEND_DIR \
    --region $REGION \
    --set-env-vars API_TOKEN=$API_TOKEN \
    --allow-unauthenticated \
    --platform managed \
    --quiet \
    --clear-base-image \
    --format="value(status.url)")
echo "Backend deploy concluído: $BACKEND_URL"

# ==========================
# ATUALIZAR .env DO FRONTEND
# ==========================
echo "Atualizando .env do frontend..."
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > $FRONTEND_DIR/.env
echo "NEXT_PUBLIC_API_TOKEN=$API_TOKEN" >> $FRONTEND_DIR/.env

# ==========================
# BUILD + DEPLOY FRONTEND via Cloud Build
# ==========================
echo "Buildando e deployando frontend usando Cloud Build..."
FRONTEND_URL=$(gcloud run deploy telegram-forward-frontend \
    --source $FRONTEND_DIR \
    --region $REGION \
    --allow-unauthenticated \
    --platform managed \
    --set-build-env-vars NODE_ENV=production \
    --quiet \
    --clear-base-image \
    --format="value(status.url)")

echo "Frontend deploy concluído: $FRONTEND_URL"

# ==========================
# FINAL
# ==========================
echo "=============================="
echo "PROJETO DEPLOYADO COM SUCESSO!"
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo "=============================="
