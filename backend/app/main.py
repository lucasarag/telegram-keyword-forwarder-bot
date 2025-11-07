from __future__ import annotations
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio

from .state import CONFIG, LOGS, ROOT, RUNTIME
from .telegram_service import SERVICE

app = FastAPI(title="Telegram Forwarder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartPayload(BaseModel):
    api_id: int
    api_hash: str
    phone: str | None = None

class ConfirmPayload(BaseModel):
    code: str
    phone: str | None = None
    password: str | None = None

class SettingsPayload(BaseModel):
    keywords: list[str]
    chat_id: int | str | None

@app.get("/api/status")
async def status():
    return {
        "is_logged": RUNTIME.get("is_logged", False),
        "keywords": CONFIG.keywords,
        "chat_id": CONFIG.chat_id,
    }

@app.post("/api/login/start")
async def login_start(p: StartPayload):
    return await SERVICE.start_login(p.api_id, p.api_hash, p.phone)

@app.post("/api/login/confirm")
async def login_confirm(p: ConfirmPayload):
    return await SERVICE.confirm_code(code=p.code, phone=p.phone, password=p.password)

@app.post("/api/settings")
async def update_settings(p: SettingsPayload):
    CONFIG.keywords = p.keywords
    CONFIG.chat_id = p.chat_id
    CONFIG.save()
    return {"ok": True}

@app.websocket("/api/ws/logs")
async def ws_logs(ws: WebSocket):
    await ws.accept()
    q = LOGS.subscribe()
    try:
        while True:
            line = await q.get()
            await ws.send_text(line)
    except WebSocketDisconnect:
        LOGS.unsubscribe(q)

@app.on_event("startup")
async def _startup():
    asyncio.create_task(SERVICE.run_forever())

# Mount frontend static files AFTER all API routes are defined
FRONTEND_DIR = ROOT / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
