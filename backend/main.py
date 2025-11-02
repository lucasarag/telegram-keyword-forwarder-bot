import asyncio
from fastapi import FastAPI, HTTPException
from telethon import TelegramClient, events
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config import settings
from utils.logger import logger

app = FastAPI(title="Telegram Forward Service")

# Estado global simples (em produção use Redis ou Firestore)
STATE = {
    "client": None,
    "running": False,
    "keyword": None,
    "target_chat": None,
    "logs": []
}

# ========== MODELOS ==========
class LoginData(BaseModel):
    api_id: int
    api_hash: str
    phone: str

class ConfigData(BaseModel):
    keyword: str
    chat_id: int

# ========== ENDPOINTS ==========

@app.post("/login")
async def login(data: LoginData):
    """Faz login e salva a sessão em memória."""
    if STATE["client"]:
        await STATE["client"].disconnect()

    client = TelegramClient("session", data.api_id, data.api_hash)
    await client.start(phone=data.phone)
    STATE["client"] = client

    logger.info("Login realizado com sucesso.")
    return {"message": "Login realizado com sucesso."}


@app.post("/config")
async def config(data: ConfigData):
    """Atualiza keyword e chat_id."""
    STATE["keyword"] = data.keyword.lower()
    STATE["target_chat"] = data.chat_id
    logger.info(f"Configuração atualizada: keyword={data.keyword}, chat={data.chat_id}")
    return {"message": "Configuração salva com sucesso."}


@app.post("/start")
async def start_forward():
    """Inicia o listener de mensagens."""
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
        log_entry = f"Recebido: {text}"
        STATE["logs"].append(log_entry)
        logger.info(log_entry)

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
    """Para o listener e desconecta o cliente."""
    if not STATE["running"]:
        raise HTTPException(400, "O listener não está em execução.")
    client: TelegramClient = STATE["client"]
    await client.disconnect()
    STATE["running"] = False
    logger.info("Forwarding parado.")
    return {"message": "Forwarding parado."}


@app.get("/logs")
async def get_logs(limit: Optional[int] = 50):
    """Retorna os últimos logs."""
    return STATE["logs"][-limit:]


@app.get("/")
def root():
    return {"status": "ok", "message": "Telegram Forward API rodando!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
