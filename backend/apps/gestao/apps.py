from django.apps import AppConfig


class GestaoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gestao"
    verbose_name = "Gestão de Usuários e Veículos"

    def ready(self):
        # Import signals when app is ready
        import apps.gestao.signals  # noqa: F401
