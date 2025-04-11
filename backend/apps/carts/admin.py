from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""

    model = CartItem
    fields = ("product", "quantity", "size", "color", "subtotal")
    readonly_fields = ("subtotal",)
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""

    list_display = (
        "id",
        "user",
        "total_items",
        "total_price",
        "created",
        "updated",
    )
    list_filter = ("created", "updated")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    date_hierarchy = "created"
    readonly_fields = ("total_price", "total_items")
    inlines = [CartItemInline]

    def total_price(self, obj):
        return obj.total_price

    def total_items(self, obj):
        return obj.total_items


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model."""

    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "size",
        "color",
        "subtotal",
        "created",
    )
    list_filter = ("created", "updated")
    search_fields = ("cart__user__email", "product__name")
    date_hierarchy = "created"
    readonly_fields = ("subtotal",)
