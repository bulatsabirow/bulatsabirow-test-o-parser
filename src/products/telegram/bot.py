import telebot
from django.conf import settings

from products.models import Product

bot = telebot.TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        f"Hello {message.chat.first_name}!\n" f"Your chat_id is {message.chat.id}",
    )


@bot.message_handler(commands=["product_list"])
def send_product_list(message):
    for text in Product.objects.fetch_numerated_product_messages():
        bot.reply_to(message, text, parse_mode="HTML")
