import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .factories import BrandFactory, CategoryFactory, ProductFactory

register(BrandFactory)
register(CategoryFactory)
register(ProductFactory)


@pytest.fixture
def api_client():
    return APIClient
