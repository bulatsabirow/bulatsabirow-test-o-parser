from django.shortcuts import render
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from products.models import Product
from products.serializers import ProductSerializer, ProductsFetchSerializer
from products.tasks import export_product_data


class ProductAPIView(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Product.objects
    lookup_field = "id"
    lookup_url_kwarg = lookup_field

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductSerializer

        return ProductsFetchSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        export_product_data.delay(serializer.data["products_count"])

        return Response(status=status.HTTP_204_NO_CONTENT)
