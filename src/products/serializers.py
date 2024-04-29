from rest_framework import serializers

from products.models import Product


class ProductsFetchSerializer(serializers.Serializer):
    products_count = serializers.IntegerField(min_value=0, max_value=50, default=10)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        excluded = ("url",)
