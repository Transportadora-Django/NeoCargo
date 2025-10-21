"""
Testes para as URLs do app Dashboard.
"""

from django.test import TestCase
from django.urls import reverse, resolve
from apps.dashboard import views


class DashboardURLsTest(TestCase):
    """Testes para as URLs do Dashboard."""

    def test_dashboard_cliente_url_resolves(self):
        """Testa se a URL do dashboard cliente resolve corretamente."""
        url = reverse("dashboard:cliente")
        self.assertEqual(url, "/dashboard/cliente/")

    def test_dashboard_cliente_url_uses_correct_view(self):
        """Testa se a URL usa a view correta."""
        url = reverse("dashboard:cliente")
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.dashboard_cliente)

    def test_dashboard_cliente_url_name(self):
        """Testa se o nome da URL está correto."""
        url = reverse("dashboard:cliente")
        resolver = resolve(url)
        self.assertEqual(resolver.url_name, "cliente")

    def test_dashboard_cliente_url_namespace(self):
        """Testa se o namespace da URL está correto."""
        url = reverse("dashboard:cliente")
        resolver = resolve(url)
        self.assertEqual(resolver.namespace, "dashboard")

    def test_dashboard_urls_pattern(self):
        """Testa se o padrão da URL está correto."""
        url = reverse("dashboard:cliente")
        self.assertTrue(url.startswith("/dashboard/"))
        self.assertTrue(url.endswith("/"))

    def test_reverse_url_without_namespace_fails(self):
        """Testa que reverter URL sem namespace gera erro."""
        with self.assertRaises(Exception):
            reverse("cliente")

    def test_invalid_dashboard_url_returns_404(self):
        """Testa que URL inválida retorna 404."""
        from django.test import Client

        client = Client()
        response = client.get("/dashboard/invalid/")
        self.assertEqual(response.status_code, 404)

    def test_dashboard_url_accepts_trailing_slash(self):
        """Testa que a URL aceita trailing slash."""
        url_with_slash = reverse("dashboard:cliente")
        self.assertTrue(url_with_slash.endswith("/"))

    def test_dashboard_url_consistency(self):
        """Testa consistência entre reverse e resolve."""
        url = reverse("dashboard:cliente")
        resolver = resolve(url)
        reversed_again = reverse(f"{resolver.namespace}:{resolver.url_name}")
        self.assertEqual(url, reversed_again)
