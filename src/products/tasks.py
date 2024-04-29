from collections.abc import Iterable

import requests
from django.conf import settings
from django.db import transaction

from products.bot.bot import bot
from products.models import Product
from products.ozon_parser.parser import OzonParser
from products.serializers import ProductSerializer
from test_o_parser.celery import app
from users.models import User


@app.task
def export_product_data(chat_id: int, products_count: int):
    print(products_count)
    ozon_parser = OzonParser(products_count)
    raw_data = ozon_parser.parse()
    products_data = [
        Product(**ProductSerializer(product_data).data) for product_data in raw_data
    ]
    with transaction.atomic():
        Product.objects.all().delete()
        Product.objects.bulk_create(products_data)
    requests.get(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": f"Задача на парсинг товаров с сайта Ozon завершена.\n"
            f"Сохранено: {products_count} товаров.",
        },
    )
