import factory

from apps.inventory.models import Brand, Category, Product


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        """Specify the model class."""

        model = Category

    name = "category_name"


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        """Specify the model class."""

        model = Brand

    name = "brand_name"


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        """Specify the model class."""

        model = Product

    name = "product_name"
    short_description = "product_short_description"
    long_description = "product_long_description"
    brand = factory.SubFactory(BrandFactory)
    category = factory.SubFactory(CategoryFactory)
