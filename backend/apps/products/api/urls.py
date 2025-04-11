from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ColorViewSet,
    ProductAdminViewSet,
    PublicCategoryViewSet,
    PublicProductViewSet,
    SizeViewSet,
)

# Router for public API endpoints
public_router = DefaultRouter()
public_router.register(r"categories", PublicCategoryViewSet)
public_router.register(r"products", PublicProductViewSet)

# Router for admin-only API endpoints
admin_router = DefaultRouter()
admin_router.register(r"categories", CategoryViewSet)
admin_router.register(r"products", ProductAdminViewSet)
admin_router.register(r"colors", ColorViewSet)
admin_router.register(r"sizes", SizeViewSet)

urlpatterns = [
    # Public API endpoints
    path("v1/products/", include(public_router.urls)),
    # Admin-only API endpoints
    path("v1/admin/products/", include(admin_router.urls)),
]
