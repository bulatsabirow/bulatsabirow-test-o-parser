from products.models import Product


def export_product_data_to_database(data):
    Product.objects.bulk_create(data)
