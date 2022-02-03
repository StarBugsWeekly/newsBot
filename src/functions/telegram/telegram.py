from crypt import methods
import os
import json
import logging
from dotenv import load_dotenv
import redis
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext 
import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class telegram():

    tg_bot           = None
    tg_updater       = None
    tg_dispatcher    = None
    redis_pool       = None
    redis_client     = None
    commands = {
        'help': '查看 Weekly StartBugs 聊天機器人的功能',
        'subscribe': '訂閱 Weekly StartBugs',
        'unsubscribe': '取消訂閱 Weekly StartBugs'
    }


    def __init__(self):
        load_dotenv()

        telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
        redis_host         = os.getenv('REDIS_HOST')
        redis_port         = os.getenv('REDIS_POST')
        redis_db           = os.getenv('REDIS_DB_SUBSCRIBE')

        self.tg_bot        = Bot(token=telegram_api_token)
        self.tg_updater    = Updater(token=telegram_api_token, use_context=True)
        self.tg_dispatcher = self.tg_updater.dispatcher

        self.redis_pool   = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)

    def send_message(self, chat_id, text):
        self.tg_bot.send_message(chat_id=chat_id, text=text)

    def go_live(self):
        self.command_handler('help', self.help)
        self.command_handler('subscribe', self.subscribe)
        self.command_handler('unsubscribe', self.unsubscribe)

        self.tg_updater.start_polling()

    def command_handler(self, command: str, handle_function: methods):
        handler = CommandHandler(command, handle_function)
        self.tg_dispatcher.add_handler(handler)

    # Define Telegram command help
    def help(self, update: Update, context: CallbackContext):
        text = ''
        for key, value in self.commands.items():
            text = text + '/' + key + ': ' + value + '\n'

        context.bot.send_message(chat_id=update.effective_chat.id, text=text)        

    # Define Telegram command subscribe
    def subscribe(self, update: Update, context: CallbackContext):

        effective_chat = update.effective_chat.to_dict()
        effective_chat["subscribe_time"] = time.time()

        self.redis_client.set(update.effective_chat.id, json.dumps(effective_chat))

        context.bot.send_message(chat_id=update.effective_chat.id, text="歡迎訂閱！ StarBugs Weekly 由一群在星空般的 Bug 中求生存的開發者所創立的週刊。每週二我們會撰寫一篇原創文章與蒐集一系列國內外的好文與大家分享。內容包含 Web 前端、後端、DevOps、產品開發、專案管理 ... 等等，一切跟產品開發有關的知識。")

    # Define Telegram command unsubscribe
    def unsubscribe(self, update: Update, context: CallbackContext):
        self.redis_client.delete(update.effective_chat.id)

        context.bot.send_message(chat_id=update.effective_chat.id, text="珍重再見，希望我們還有相遇的一天 T_T")

    # Define Telegram command weekly
    #def weekly():

    # Define Telegram command recommand
    #def recommand():    