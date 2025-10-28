# Telegram Keyword Forwarder Bot

Este projeto implementa um bot para Telegram que monitora mensagens recebidas em chats (privados ou grupos) e encaminha automaticamente aquelas que contenham palavras-chave específicas para um chat definido.  
O sistema é desenvolvido em **Python**, utiliza a biblioteca **python-telegram-bot** e é totalmente containerizado com **Docker** e **Docker Compose**.  
Os registros de execução e eventos são mantidos em arquivos de log persistentes.

---

## 1. Funcionalidades

- Leitura de todas as mensagens recebidas (texto e mídia com legenda)  
- Detecção de palavras-chave (case-insensitive)  
- Encaminhamento automático das mensagens que correspondam aos critérios  
- Registro detalhado em log, incluindo remetente, conteúdo, chat e horário  
- Configuração simplificada por variáveis de ambiente (.env)  
- Execução isolada em container Docker  

---

## 3. Requisitos

- Python 3.10+ (caso queira executar localmente)
- Docker
- Docker Compose
- Um bot criado através do **@BotFather** no Telegram

---

## 4. Criação do Bot

1. No Telegram, abra o chat com **@BotFather**  
2. Envie o comando `/newbot`  
3. Escolha o nome e o username do bot  
4. Copie o token de autenticação fornecido; ele será utilizado na configuração do projeto  

---

## 5. Identificação do Chat ID

O **chat_id** é o identificador único de cada conversa (chat privado, grupo ou canal) no Telegram.  
Ele define para onde as mensagens serão encaminhadas.

### 5.1. Descobrir Chat ID de um Usuário
1. Inicie o bot no Telegram e envie o comando `/start`  
2. Execute o container do bot e verifique os logs gerados  
3. O log exibirá o ID do chat na linha correspondente à mensagem recebida  

Alternativamente, é possível obter o chat ID utilizando o bot **@userinfobot**.  
Após enviar `/start`, o bot responderá com o identificador do seu usuário.

### 5.2. Chat ID de um Grupo
1. Adicione o bot ao grupo  
2. Envie uma mensagem qualquer no grupo  
3. Verifique os logs do bot. O campo “Chat” exibirá o nome e o ID (geralmente iniciado com `-100`)

---

## 6. Configuração (.env)

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```bash
BOT_TOKEN=123456:ABCdefGHIjklMNOpqrSTUvwxYZ
MY_CHAT_ID=123456789
KEYWORDS=alarme,urgente,erro,teste
```

## 7. Execução com Docker Compose

### 7.1. Construção e inicialização

```docker compose up -d --build```

### 7.2. Verificação de logs em tempo real

```docker compose logs -f```

### 7.3. Interrupção do serviço

```docker compose down```

## 8. Logs

Os registros de execução são gravados em logs/bot.log.
Cada entrada contém informações detalhadas sobre mensagens detectadas e encaminhadas, incluindo usuário, texto, chat e data/hora.

------------------------------------------------------------

## 9. Execução Local (sem Docker)

Para execução direta com Python:
```
pip install python-telegram-bot==20.6
BOT_TOKEN="..." MY_CHAT_ID="..." python keyword_forwarder_bot.py
```

## 10. Personalizações

1. Alterar palavras-chave: edite a variável KEYWORDS no arquivo .env

2. Limitar a mensagens de texto: substitua filters.ALL por filters.TEXT no script principal

3. Alterar destino de encaminhamento: modifique o valor de MY_CHAT_ID

## 11. Modo de Privacidade do Bot

Por padrão, os bots no Telegram têm o modo de privacidade ativado, o que impede que leiam todas as mensagens em grupos.
Para desativá-lo:

1. No chat com o @BotFather, envie /setprivacy

2. Escolha o seu bot

3. Selecione Disable

Isso permite que o bot processe todas as mensagens no grupo.