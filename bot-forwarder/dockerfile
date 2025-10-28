FROM python:3.11-slim
WORKDIR /app

COPY keyword_forwarder_bot.py ./

RUN pip install --no-cache-dir python-telegram-bot==20.6 tzdata

# cria diretório de logs
RUN mkdir -p /app/logs

ENV BOT_TOKEN=""
ENV MY_CHAT_ID=""
ENV KEYWORDS="alarme,urgente,erro"

CMD ["python", "keyword_forwarder_bot.py"]
