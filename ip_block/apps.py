from django.apps import AppConfig


class IpBlockConfig(AppConfig):
    """App config for the IP Block middleware."""

    name = "ip_block"
    verbose_name = "IP Block"
    default_auto_field = "django.db.models.BigAutoField"
