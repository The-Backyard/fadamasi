from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Swagger Doc URL
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
    # 3rd party URL
    path("silk/", include("silk.urls", namespace="silk")),
    # App API URL
    path("api/", include("apps.accounts.api.urls")),
    path("api/", include("apps.carts.api.urls")),
    path("api/", include("apps.products.api.urls")),
    path("", include("apps.core.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

admin.site.site_header = "Fadamasi Concept Ecommerce"
admin.site.index_title = "Fadamasi Concept Ecommerce"
admin.site.site_title = "Fadamasi Concept Ecommerce Administration"
