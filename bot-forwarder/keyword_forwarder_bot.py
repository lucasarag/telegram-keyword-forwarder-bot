import os
import re
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ========= CONFIGURAÇÕES =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID"))
KEYWORDS = [kw.strip().lower() for kw in os.getenv("KEYWORDS", "").split(",") if kw.strip()]

# ========= LOGGING =========
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("Bot iniciado. Aguardando mensagens...")

def contains_keyword(text: str) -> bool:
    """Verifica se o texto contém alguma das palavras-chave (case-insensitive)."""
    if not text:
        return False
    text_lower = text.lower()
    for kw in KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", text_lower):
            return True
    return False


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg is None:
        return

    text = msg.text or msg.caption
    if not text:
        return

    user = msg.from_user
    username = f"@{user.username}" if user and user.username else user.full_name if user else "Desconhecido"
    chat_title = msg.chat.title if msg.chat.type in ["group", "supergroup"] else "Chat Privado"
    chat_id = msg.chat.id

    if contains_keyword(text):
        try:
            await context.bot.forward_message(
                chat_id=MY_CHAT_ID,
                from_chat_id=chat_id,
                message_id=msg.message_id
            )
            log_entry = (
                f"Palavra-chave detectada!\n"
                f"👤 Usuário: {username}\n"
                f"💬 Mensagem: {text}\n"
                f"🏷️ Chat: {chat_title} (ID: {chat_id})\n"
                f"🕒 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{'-'*60}"
            )
            logger.info(log_entry)

        except Exception as e:
            logger.exception(f"Erro ao encaminhar mensagem: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Lê todas as mensagens (texto, mídias com caption etc.)
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.run_polling()
