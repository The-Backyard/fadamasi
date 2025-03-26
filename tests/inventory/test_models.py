import pytest

pytestmark = pytest.mark.django_db


class TestBrandModel:
    def test_str_method(self, brand_factory):
        brand = brand_factory(name="brand-1")
        assert brand.__str__() == "brand-1"


class TestCategoryModel:
    def test_str_method(self, category_factory):
        category = category_factory(name="cat-1")
        assert category.__str__() == "cat-1"


class TestProductModel:
    def test_str_method(self, product_factory):
        product = product_factory(name="product-1")
        assert product.__str__() == "product-1"
