import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from datetime import datetime

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS").split(",")]
FORWARD_CHAT_ID = int(os.getenv("FORWARD_CHAT_ID"))
LOG_FILE = "logs/bot.log"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def log_message(entry):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n" + "-"*60 + "\n")

@client.on(events.NewMessage(incoming=True, chats=None))
async def handler(event):
    message = event.message
    message_text = message.message or "<sem texto>"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Informações do remetente e chat
    sender = await event.get_sender()
    chat = await event.get_chat()
    sender_name = getattr(sender, 'username', None) or str(sender.id)
    chat_name = getattr(chat, 'title', None) or str(chat.id)

    # Log de TODAS as mensagens
    log_entry = (
        f"[{timestamp}] Nova mensagem recebida\n"
        f"Remetente: {sender_name}\n"
        f"Chat: {chat_name}\n"
        f"Mensagem: {message_text}"
    )
    log_message(log_entry)
    print(log_entry, flush=True)


    # Filtra por palavras-chave
    msg_lower = message_text.lower()
    for kw in KEYWORDS:
        if kw in msg_lower:
            forward_entry = f"[{timestamp}] Palavra-chave detectada: '{kw}' - Mensagem encaminhada"
            log_message(forward_entry)
            print(forward_entry, flush=True)
            await client.send_message(FORWARD_CHAT_ID, message_text)
            break

print("User forwarder iniciado...")
client.start()
client.run_until_disconnected()
