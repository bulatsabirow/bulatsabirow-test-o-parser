from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from products.models import Product
from products.permissions import ProductsPermission
from products.serializers import ProductSerializer, ProductsFetchSerializer
from products.tasks import export_product_data


class ProductAPIView(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Product.objects
    lookup_field = "id"
    lookup_url_kwarg = lookup_field
    permission_classes = (ProductsPermission,)
    authentication_classes = [BasicAuthentication]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductSerializer

        return ProductsFetchSerializer

    @swagger_auto_schema(responses={status.HTTP_204_NO_CONTENT: ""})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        export_product_data.delay(
            request.user.telegram_id, serializer.data["products_count"]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
