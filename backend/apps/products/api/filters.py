import django_filters

from apps.products.models import Product


class ProductFilter(django_filters.FilterSet):
    class Meta:
        """Meta options for the custom Product filter."""

        model = Product
        fields = {
            "name": ["iexact", "icontains"],
            "price": ["exact", "lt", "gt", "range"],
        }
