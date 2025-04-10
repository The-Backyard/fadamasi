from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartItemViewSet, CartViewSet

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"cart-items", CartItemViewSet, basename="cart-items")

urlpatterns = [
    path("v1/", include(router.urls)),
]
