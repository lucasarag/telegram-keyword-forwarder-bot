# Telegram Keyword Forwarder

Este projeto cria um bot que monitora mensagens em chats do Telegram e encaminha mensagens que contenham certas palavras-chave para outro chat.

---

### Pré-requisitos

- Python 3.10 ou superior
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- Conta no Telegram e API_ID/API_HASH
- Docker (para rodar via container, opcional)

---

### Configuração

###  1. Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd telegram-keyword-forwarder
```

### 2. Crie um arquivo `.env` com as variáveis de ambiente:

```env
API_ID=seu_api_id
API_HASH=seu_api_hash
STRING_SESSION=sua_string_session
FORWARD_CHAT_ID=chat_destino
KEYWORDS=Samsung,S23,S24,S25,Iphone
```

> Observação: Separe múltiplas palavras-chave por vírgula.

### 3. Instale as dependências:

```bash
pip install -r requirements.txt
```

---

### Rodando localmente

```bash
python user_forwarder.py
```

---

### Rodando via Docker

### 1. Build da imagem:

```bash
docker build -t telegram-forwarder .
```

### 2. Rodar o container:

```bash
docker run --env-file .env telegram-forwarder
```

---

### Deploy no Google Cloud Run

### 1. Build e push da imagem para Google Container Registry:

```bash
gcloud builds submit --tag gcr.io/<PROJETO>/telegram-forwarder
```

### 2. Criar o job no Cloud Run:

```bash
gcloud beta run jobs create telegram-user-forwarder \
    --image gcr.io/<PROJETO>/telegram-forwarder \
    --region us-central1 \
    --env-vars-file .env
```

### 3. Executar o job:

```bash
gcloud beta run jobs execute telegram-user-forwarder --region us-central1
```

### 4. Ver logs:

```bash
gcloud logs read --project=<PROJETO> --limit=50
```

---

### Observações

- Cada `STRING_SESSION` só pode ser usado por uma instância do bot por vez.
- Ao atualizar o código, lembre-se de rebuildar e subir a nova imagem.
- Evite usar variáveis com caracteres especiais sem aspas no `.env`.

---

### Referências

- [Telethon](https://docs.telethon.dev/)
- [Google Cloud Run Jobs](https://cloud.google.com/run/docs)
- [Google Cloud Pub/Sub](https://cloud.google.com/pubsub/docs)
