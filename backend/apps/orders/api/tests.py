from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from apps.orders.models import Order

User = get_user_model()


class UserOrderTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username="user1", password="test1")  # noqa: S106
        user2 = User.objects.create_user(username="user2", password="test2")  # noqa: S106
        Order.objects.create(user=user1)
        Order.objects.create(user=user1)
        Order.objects.create(user=user2)
        Order.objects.create(user=user2)

    def test_user_order_endpoint_retrieves_only_authenticated_user_orders(self):
        user = User.objects.get(username="user1")
        self.client.force_login(user)
        response = self.client.get(reverse("user_order_list"))
        assert response.status_code == status.HTTP_200_OK
        orders = response.json()
        self.assertTrue(all(order["user"] == user.id for order in orders))

    def test_user_order_list_unauthenticated(self):
        response = self.client.get(reverse("user_order_list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
