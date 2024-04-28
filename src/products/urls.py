from django.urls import include, path
from rest_framework import routers

from products.views import ProductAPIView, ProductsFetchAPIView

router = routers.DefaultRouter()
router.register(r"products", ProductAPIView, basename="products")

urlpatterns = [
    path("products/", ProductsFetchAPIView.as_view(), name="products-fetch"),
    *router.urls,
]
