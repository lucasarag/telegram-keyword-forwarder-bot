import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

async def list_chats():
    await client.start()
    print("Listando todos os chats, grupos e canais da conta:\n")
    async for dialog in client.iter_dialogs():
        chat_type = "Canal" if dialog.is_channel else "Grupo/Privado"
        print(f"Nome: {dialog.name} | ID: {dialog.id} | Tipo: {chat_type}")

with client:
    client.loop.run_until_complete(list_chats())
