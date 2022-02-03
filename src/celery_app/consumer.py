import os
from celery_app import newsBot
from dotenv import load_dotenv
from functions.telegram.telegram import telegram

bot = telegram()

@newsBot.task
def send_message(chat_id, text):
    bot.send_message(chat_id, text)
    