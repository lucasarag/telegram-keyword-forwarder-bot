import os
import asyncio
from fastapi import FastAPI, HTTPException, Request
from telethon import TelegramClient, events
from pydantic import BaseModel
from typing import Optional

from utils.logger import logger  # seu logger customizado

# ==========================
# TOKEN DE AUTENTICAÇÃO
# ==========================
API_TOKEN = os.environ.get("API_TOKEN", "")
if not API_TOKEN:
    raise ValueError("API_TOKEN não definido nas variáveis de ambiente")

# ==========================
# APP FASTAPI
# ==========================
app = FastAPI(title="Telegram Forward Service")

# ==========================
# ESTADO GLOBAL
# ==========================
STATE = {
    "client": None,
    "running": False,
    "keyword": None,
    "target_chat": None,
    "logs": []
}

# ==========================
# MODELOS
# ==========================
class LoginData(BaseModel):
    api_id: int
    api_hash: str
    phone: str

class ConfigData(BaseModel):
    keyword: str
    chat_id: int

# ==========================
# MIDDLEWARE TOKEN
# ==========================
@app.middleware("http")
async def verify_token(request: Request, call_next):
    token = request.headers.get("x-api-token")
    if token != API_TOKEN:
        return HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

# ==========================
# ENDPOINTS
# ==========================
@app.post("/login")
async def login(data: LoginData):
    if STATE["client"]:
        await STATE["client"].disconnect()

    client = TelegramClient("session", data.api_id, data.api_hash)
    await client.start(phone=data.phone)
    STATE["client"] = client

    logger.info("Login realizado com sucesso.")
    return {"message": "Login realizado com sucesso."}


@app.post("/config")
async def config(data: ConfigData):
    STATE["keyword"] = data.keyword.lower()
    STATE["target_chat"] = data.chat_id
    logger.info(f"Configuração atualizada: keyword={data.keyword}, chat={data.chat_id}")
    return {"message": "Configuração salva com sucesso."}


@app.post("/start")
async def start_forward():
    if STATE["running"]:
        raise HTTPException(400, "O listener já está em execução.")

    client: TelegramClient = STATE["client"]
    if not client:
        raise HTTPException(400, "Cliente não autenticado. Faça login primeiro.")

    keyword = STATE["keyword"]
    target_chat = STATE["target_chat"]
    if not keyword or not target_chat:
        raise HTTPException(400, "Configure keyword e chat_id antes de iniciar.")

    @client.on(events.NewMessage)
    async def handler(event):
        text = event.message.message or ""
        STATE["logs"].append(f"Recebido: {text}")
        logger.info(f"Recebido: {text}")
        if keyword in text.lower():
            await client.send_message(target_chat, event.message)
            STATE["logs"].append(f"✅ Encaminhado: {text}")
            logger.info(f"✅ Encaminhado: {text}")

    STATE["running"] = True
    asyncio.create_task(client.run_until_disconnected())
    logger.info("Forwarding iniciado.")
    return {"message": "Forwarding iniciado."}


@app.post("/stop")
async def stop_forward():
    if not STATE["running"]:
        raise HTTPException(400, "O listener não está em execução.")
    client: TelegramClient = STATE["client"]
    await client.disconnect()
    STATE["running"] = False
    logger.info("Forwarding parado.")
    return {"message": "Forwarding parado."}


@app.get("/logs")
async def get_logs(limit: Optional[int] = 50):
    return STATE["logs"][-limit:]


@app.get("/status")
async def status():
    return {
        "client_connected": STATE["client"] is not None,
        "forwarding": STATE["running"],
        "keyword": STATE["keyword"],
        "target_chat": STATE["target_chat"]
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "Telegram Forward API rodando!"}


# ==========================
# Uvicorn para Cloud Run
# ==========================
if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 8080))  # Cloud Run define essa variável
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
