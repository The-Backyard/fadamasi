from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.orders.models import Order

from .serializers import OrderSerializer


class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related(
        "items__product",
    )
    serializer_class = OrderSerializer


class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related(
        "items__product",
    )
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
