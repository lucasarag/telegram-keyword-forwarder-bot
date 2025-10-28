#!/bin/bash
set -e

# ==========================
# CONFIGURAÇÃO
# ==========================
PROJECT_ID="telegram-keyword-forwarder"
REGION="us-central1"
SERVICE_NAME="telegram-user-forwarder"
SCHEDULE_NAME="telegram-forwarder-scheduler"
CRON_SCHEDULE="*/5 * * * *"   # Executa a cada 5 minutos
ENV_FILE=".env"
DOCKER_IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

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
# BUILD DOCKER SE NECESSÁRIO
# ==========================
BUILD_HASH=$(sha256sum Dockerfile $ENV_FILE | awk '{print $1}' | sha256sum | awk '{print $1}')
LAST_BUILD_HASH_FILE=".last_build_hash"

REBUILD=false
if [ ! -f "$LAST_BUILD_HASH_FILE" ] || [ "$BUILD_HASH" != "$(cat $LAST_BUILD_HASH_FILE)" ]; then
    REBUILD=true
fi

if [ "$REBUILD" = true ]; then
    echo "Mudanças detectadas. Construindo imagem Docker..."
    gcloud builds submit --tag $DOCKER_IMAGE .
    echo $BUILD_HASH > $LAST_BUILD_HASH_FILE
else
    echo "Nenhuma mudança detectada. Pulando build do Docker."
fi

# ==========================
# CRIAR OU ATUALIZAR JOB
# ==========================
JOB_EXISTS=$(gcloud beta run jobs list --region $REGION --format="value(metadata.name)" | grep "^$SERVICE_NAME$" || true)

if [ -z "$JOB_EXISTS" ]; then
    echo "Criando Job..."
    gcloud beta run jobs create $SERVICE_NAME \
        --image $DOCKER_IMAGE \
        --region $REGION \
        --env-vars-file $ENV_FILE
else
    echo "Atualizando Job existente..."
    gcloud beta run jobs update $SERVICE_NAME \
        --image $DOCKER_IMAGE \
        --region $REGION \
        --env-vars-file $ENV_FILE
fi

# ==========================
# CONFIGURAR PERMISSÕES
# ==========================
SERVICE_ACCOUNT="$PROJECT_ID@appspot.gserviceaccount.com"

if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project "$PROJECT_ID" >/dev/null 2>&1; then
    echo "Erro: conta de serviço $SERVICE_ACCOUNT não existe."
    echo "Crie o App Engine antes de prosseguir: gcloud app create --region=$REGION"
    exit 1
fi

gcloud run jobs add-iam-policy-binding $SERVICE_NAME \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.invoker" \
    --region $REGION

# ==========================
# CRIAR OU ATUALIZAR CLOUD SCHEDULER
# ==========================
SCHEDULER_EXISTS=$(gcloud scheduler jobs list --location=$REGION --project $PROJECT_ID --filter="NAME:$SCHEDULE_NAME" --format="value(name)" || true)

SCHEDULER_URI="https://run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$SERVICE_NAME:run"

if [ -z "$SCHEDULER_EXISTS" ]; then
    echo "Criando Cloud Scheduler..."
    gcloud scheduler jobs create http $SCHEDULE_NAME \
        --schedule="$CRON_SCHEDULE" \
        --time-zone="UTC" \
        --uri="$SCHEDULER_URI" \
        --http-method=POST \
        --oauth-service-account-email="$SERVICE_ACCOUNT" \
        --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform" \
        --location="$REGION"
else
    echo "Atualizando Cloud Scheduler existente..."
    gcloud scheduler jobs update http $SCHEDULE_NAME \
        --schedule="$CRON_SCHEDULE" \
        --time-zone="UTC" \
        --uri="$SCHEDULER_URI" \
        --http-method=POST \
        --oauth-service-account-email="$SERVICE_ACCOUNT" \
        --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform" \
        --location="$REGION"
fi

# ==========================
# FINALIZAÇÃO
# ==========================
echo
echo "✅ Deploy concluído com sucesso!"
echo "──────────────────────────────────────────────"
echo "Projeto:   $PROJECT_ID"
echo "Região:    $REGION"
echo "Job:       $SERVICE_NAME"
echo "Scheduler: $SCHEDULE_NAME"
echo "Execução:  $CRON_SCHEDULE (UTC)"
echo "Logs:      https://console.cloud.google.com/run/jobs/details/$REGION/$SERVICE_NAME/logs?project=$PROJECT_ID"
echo "──────────────────────────────────────────────"

gcloud beta run jobs execute $SERVICE_NAME --region us-central1