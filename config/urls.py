from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from apps.inventory import views

router = DefaultRouter()
router.register(r"brand", views.BrandViewSet)
router.register(r"category", views.CategoryViewSet)
router.register(r"product", views.ProductViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/auth/", include("apps.account.urls")),
    path("api/", include(router.urls)),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )

admin.site.site_header = "Fadamasi Concept Ecommerce"
admin.site.index_title = "Fadamasi Concept Ecommerce"
admin.site.site_title = "Fadamasi Concept Ecommerce Administration"
