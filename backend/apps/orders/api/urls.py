from django.urls import path

from . import views

urlpatterns = [
    path("user/", views.UserOrderListAPIView.as_view(), name="user_order_list"),
    path("", views.OrderListAPIView.as_view(), name="order_list"),
]
