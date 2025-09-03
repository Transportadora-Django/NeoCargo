from django.apps import AppConfig


class ContasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contas"
    verbose_name = "Contas"

    def ready(self):
        import apps.contas.signals  # noqa
