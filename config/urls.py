from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
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
