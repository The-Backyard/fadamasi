from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RootAPITestCase(APITestCase):
    def test_root_api_returns_successful_response(self):
        """Ensure the root API returns a successful response."""
        url = reverse("root_api")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Fadamasi Backend API Setup"})
