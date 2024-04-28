from collections.abc import Iterable

from products.models import Product
from products.ozon_parser.parser import OzonParser
from products.serializers import ProductSerializer
from test_o_parser.celery import app


@app.task
def export_product_data(products_count: int):
    ozon_parser = OzonParser(products_count)
    raw_data = ozon_parser.parse()
    products_data = [
        Product(**ProductSerializer(product_data).data) for product_data in raw_data
    ]
    Product.objects.bulk_create(products_data)
