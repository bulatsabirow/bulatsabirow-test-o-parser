from collections.abc import Iterable

from products.models import Product
from products.ozon_parser.parser import OzonParser
from test_o_parser.celery import app


@app.task
def export_product_data(products_count: int):
    ozon_parser = OzonParser(products_count)
    products_data = ozon_parser.parse()
    Product.objects.bulk_create(products_data)
