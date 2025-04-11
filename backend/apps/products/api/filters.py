import django_filters
from django.db.models import Q

from apps.products.models import Category, Product


class ProductFilter(django_filters.FilterSet):
    """Filter class for advanced product filtering."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name="category",
    )
    category_slug = django_filters.CharFilter(field_name="category__slug")
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )
    gender = django_filters.CharFilter(method="filter_gender")
    color = django_filters.CharFilter(
        field_name="colors__name",
        lookup_expr="iexact",
    )
    size = django_filters.CharFilter(
        field_name="sizes__name",
        lookup_expr="iexact",
    )
    is_available = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    is_discounted = django_filters.BooleanFilter(method="filter_discounted")
    search = django_filters.CharFilter(method="filter_search")

    def filter_gender(self, queryset, name, value):
        if value:
            # Allow for both full gender name and single letter
            if value.lower() in ["male", "m"]:
                return queryset.filter(gender="M")
            if value.lower() in ["female", "f"]:
                return queryset.filter(gender="F")
            if value.lower() in ["unisex", "u"]:
                return queryset.filter(gender="U")
        return queryset

    def filter_discounted(self, queryset, name, value):
        if value:
            return queryset.filter(discount_price__isnull=False)
        return queryset

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value)
                | Q(description__icontains=value)
                | Q(category__name__icontains=value)
                | Q(meta_keywords__icontains=value)
            )
        return queryset

    class Meta:
        """Meta class to define the model and fields for the ProductFilter."""

        model = Product
        fields = [
            "name",
            "category",
            "category_slug",
            "min_price",
            "max_price",
            "gender",
            "color",
            "size",
            "is_available",
            "is_featured",
        ]
