import telebot
from django.conf import settings

bot = telebot.TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        f"Hello {message.chat.first_name}!\n" f"Your chat_id is {message.chat.id}",
    )
