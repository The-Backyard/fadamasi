from django.apps import AppConfig


class CartsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.carts"
    verbose_name = "Shopping Cart"

    def ready(self):
        import apps.carts.signals  # noqa: F401
