from django.urls import path

from . import views

urlpatterns = [
    path("info/", views.ProductInfoAPIView.as_view(), name="product_info"),
    path(
        "<int:pk>/",
        views.ProductDetailAPIView.as_view(),
        name="product_detail",
    ),
    path("", views.ProductListCreateAPIView.as_view(), name="product_create_list"),
]
