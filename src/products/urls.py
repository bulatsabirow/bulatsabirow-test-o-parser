from django.urls import include, path
from rest_framework import routers

from products.views import ProductAPIView

router = routers.DefaultRouter()
router.register(r"products", ProductAPIView, basename="products")

urlpatterns = [
    *router.urls,
]
