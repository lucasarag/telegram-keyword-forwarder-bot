from __future__ import annotations
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from typing import Optional, List
import asyncio
import uuid

from .state import CONFIG, LOGS, DATA_DIR, RUNTIME

SESSION_DIR = DATA_DIR / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

class TelegramService:
    def __init__(self) -> None:
        self.client: Optional[TelegramClient] = None
        self.lock = asyncio.Lock()

    async def _log(self, msg: str) -> None:
        await LOGS.publish(msg)

    async def start_login(self, api_id: int, api_hash: str, phone: str | None) -> dict:
        async with self.lock:
            session_id = str(uuid.uuid4())
            session_path = SESSION_DIR / f"{session_id}.session"
            await self._log(f"[login] iniciando sessão {session_id}")

            try:
                # Create client with auto-reconnect enabled
                self.client = TelegramClient(
                    str(session_path),
                    api_id,
                    api_hash,
                    connection_retries=5,
                    retry_delay=1,
                    auto_reconnect=True
                )
                
                # Connect without checking authorization first (to avoid CancelledError)
                await self._log("[login] conectando ao Telegram...")
                await self.client.connect()
                
                # Wait a bit for connection to stabilize
                await asyncio.sleep(1)

                # Check if already authorized
                try:
                    if await self.client.is_user_authorized():
                        await self._log("[login] sessão já autorizada")
                        RUNTIME.update({"session_id": session_id, "is_logged": True})
                        await self._install_handlers()
                        return {"status": "already_logged", "session_id": session_id}
                except asyncio.CancelledError:
                    await self._log("[login] verificação de autorização cancelada, continuando com login...")
                    pass

                if not phone:
                    await self._log("[login] telefone não informado; necessário para enviar o código")
                    return {"status": "phone_required"}

                # Send code request
                await self._log(f"[login] enviando código para {phone}...")
                sent = await self.client.send_code_request(phone)
                await self._log(f"[login] código enviado para {phone}")
                RUNTIME.update({"session_id": session_id})
                return {"status": "code_sent", "session_id": session_id}
                
            except asyncio.CancelledError:
                await self._log(f"[login] operação cancelada, isso pode indicar migração de DC")
                return {"error": "Operação cancelada. Tente novamente em alguns segundos."}
            except Exception as e:
                await self._log(f"[login] erro: {e}")
                return {"error": str(e)}

    async def confirm_code(self, code: str, phone: str | None = None, password: str | None = None) -> dict:
        async with self.lock:
            if not self.client:
                return {"error": "client_not_initialized"}

            try:
                # Ensure connection before signing in
                if not self.client.is_connected():
                    await self.client.connect()
                    await asyncio.sleep(0.5)
                
                if password:  # 2FA
                    await self.client.sign_in(password=password)
                else:
                    await self.client.sign_in(code=code)
                RUNTIME["is_logged"] = True
                await self._log("[login] sessão autenticada com sucesso")
                await self._install_handlers()
                return {"status": "logged"}

            except SessionPasswordNeededError:
                await self._log("[login] 2FA necessário — envie a senha")
                return {"status": "password_required"}

            except Exception as e:
                await self._log(f"[login] erro: {e}")
                return {"error": str(e)}

    async def _install_handlers(self) -> None:
        assert self.client is not None

        @self.client.on(events.NewMessage)
        async def on_message(event):
            try:
                text = event.message.message or ""
                await self._log(f"[recv] {event.chat_id}: {text}")

                lowered = text.lower()
                keywords: List[str] = [k.strip().lower() for k in CONFIG.keywords]
                if keywords and any(k in lowered for k in keywords):
                    if CONFIG.chat_id:
                        try:
                            target = CONFIG.chat_id
                            
                            # Try different approaches to send the message
                            # 1. If it starts with @, use as username
                            if isinstance(target, str) and target.startswith('@'):
                                await self.client.send_message(target, text)
                                await self._log(f"[fwd] → {target}: {text}")
                            # 2. If it's a string that looks like a phone number, try with +
                            elif isinstance(target, str) and target.isdigit() and len(target) >= 10:
                                # Try with + prefix for phone numbers
                                phone_target = f"+{target}"
                                await self._log(f"[fwd] tentando enviar para telefone {phone_target}...")
                                await self.client.send_message(phone_target, text)
                                await self._log(f"[fwd] → {phone_target}: {text}")
                            # 3. Try as numeric ID
                            else:
                                target_id = int(target) if isinstance(target, str) else target
                                await self.client.send_message(target_id, text)
                                await self._log(f"[fwd] → {target_id}: {text}")
                                
                        except ValueError as ve:
                            await self._log(f"[error] chat_id inválido '{CONFIG.chat_id}': {ve}")
                        except Exception as send_error:
                            await self._log(f"[error] falha ao enviar para {CONFIG.chat_id}: {send_error}")
                            await self._log(f"[dica] Certifique-se de que o chat_id está correto. Use @username, +telefone ou ID numérico")
                    else:
                        await self._log("[warn] chat_id não configurado; mensagem não encaminhada")

            except Exception as e:
                await self._log(f"[handler_error] {e}")

        await self.client.start()
        await self._log("[runtime] handlers instalados e cliente iniciado")

    async def get_dialogs(self) -> list:
        """Get list of recent chats/dialogs to help find the correct chat_id"""
        if not self.client or not self.client.is_connected():
            return []
        
        try:
            dialogs = []
            async for dialog in self.client.iter_dialogs(limit=50):
                dialogs.append({
                    "id": dialog.id,
                    "name": dialog.name,
                    "title": dialog.title if hasattr(dialog, 'title') else dialog.name,
                    "is_user": dialog.is_user,
                    "is_group": dialog.is_group,
                    "is_channel": dialog.is_channel,
                })
            return dialogs
        except Exception as e:
            await self._log(f"[error] falha ao obter diálogos: {e}")
            return []

    async def run_forever(self) -> None:
        while True:
            try:
                if self.client and self.client.is_connected():
                    await self.client.run_until_disconnected()
                    await self._log("[runtime] cliente desconectado, aguardando reconexão...")
                else:
                    await asyncio.sleep(5)
            except ConnectionError as e:
                await self._log(f"[runtime] erro de conexão: {e}, tentando reconectar em 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                await self._log(f"[runtime] erro inesperado: {e}")
                await asyncio.sleep(5)

SERVICE = TelegramService()
