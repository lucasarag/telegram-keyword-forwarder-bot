from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from telethon import TelegramClient
import os
import asyncio

api_id = os.getenv("API_ID", "123456")  # coloque o seu API ID
api_hash = os.getenv("API_HASH", "abcdef1234567890")  # coloque o seu API HASH

app = FastAPI()

# 🔧 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Modelos
class LoginRequest(BaseModel):
    phone: str
    code: str | None = None

# Armazena sessão e cliente
clients = {}
pending_logins = {}

@app.post("/login")
async def login(data: LoginRequest):
    phone = data.phone
    code = data.code
    session_name = f"sessions/{phone.replace('+', '')}"

    os.makedirs("sessions", exist_ok=True)

    client = TelegramClient(session_name, api_id, api_hash)

    # Se ainda não iniciou o login, envia código
    if phone not in pending_logins and code is None:
        await client.connect()
        await client.send_code_request(phone)
        pending_logins[phone] = client
        return {"message": "Código enviado para o Telegram!"}

    # Se o código foi recebido, tenta finalizar login
    elif phone in pending_logins and code is not None:
        client = pending_logins[phone]
        try:
            await client.connect()
            await client.sign_in(phone=phone, code=code)
            clients[phone] = client
            del pending_logins[phone]
            return {"message": "Login realizado com sucesso!"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Fluxo de login incorreto.")


@app.get("/")
def home():
    return {"status": "ok"}
