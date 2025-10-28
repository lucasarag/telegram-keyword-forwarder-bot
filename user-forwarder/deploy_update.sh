#!/bin/bash
set -e

# ==========================================================
# CONFIGURAÇÕES DO PROJETO
# ==========================================================
PROJECT_ID="telegram-keyword-forwarder"
REGION="us-central1"
JOB_NAME="telegram-user-forwarder"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${JOB_NAME}"
ENV_FILE=".env"

# ==========================================================
# VERIFICA SE O .env EXISTE
# ==========================================================
if [ ! -f "$ENV_FILE" ]; then
  echo "ERRO: O arquivo .env não foi encontrado no diretório atual."
  echo "Crie um arquivo .env com as variáveis necessárias."
  exit 1
fi

# ==========================================================
# FAZ O BUILD E O PUSH DA NOVA IMAGEM
# ==========================================================
echo "🔨 Buildando e enviando nova imagem Docker..."
gcloud builds submit --tag "$IMAGE_NAME" .

# ==========================================================
# CARREGA VARIÁVEIS DE AMBIENTE DO .env
# ==========================================================
echo "🔧 Lendo variáveis de ambiente do .env..."
ENV_VARS=$(grep -v '^#' "$ENV_FILE" | xargs | sed 's/ /,/g')

# ==========================================================
# ATUALIZA O JOB EXISTENTE
# ==========================================================
echo "🚀 Atualizando job ${JOB_NAME} no Cloud Run..."
gcloud beta run jobs update "$JOB_NAME" \
  --image "$IMAGE_NAME" \
  --region "$REGION" \
  --update-env-vars "$ENV_VARS"

# ==========================================================
# EXECUTA O JOB
# ==========================================================
echo "▶️ Executando o job atualizado..."
EXECUTION_NAME=$(gcloud beta run jobs execute "$JOB_NAME" \
  --region "$REGION" \
  --format="value(metadata.name)")

# ==========================================================
# EXIBE LINK PARA OS LOGS
# ==========================================================
echo ""
echo "==============================================="
echo "✅ Deploy concluído com sucesso!"
echo "🔍 Acompanhe os logs em tempo real aqui:"
echo "https://console.cloud.google.com/logs/viewer?project=${PROJECT_ID}&advancedFilter=resource.type%3D%22cloud_run_job%22%0Aresource.labels.job_name%3D%22${JOB_NAME}%22%0Aresource.labels.location%3D%22${REGION}%22%0Alabels.%22run.googleapis.com/execution_name%22%3D%22${EXECUTION_NAME}%22"
echo "==============================================="
