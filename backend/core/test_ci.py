"""
Testes básicos para verificar o funcionamento do CI.
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CITestCase(TestCase):
    """Testes simples para validar o CI."""

    def test_django_installation(self):
        """Testa se o Django está funcionando corretamente."""
        from django.conf import settings

        self.assertTrue(hasattr(settings, "SECRET_KEY"))
        self.assertIsNotNone(settings.SECRET_KEY)

    def test_database_connection(self):
        """Testa se a conexão com o banco está funcionando."""
        # Criar um usuário simples para testar o banco
        user = User.objects.create_user(username="testuser", email="test@neocargo.com", password="testpass123")

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@neocargo.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_admin_url_exists(self):
        """Testa se a URL do admin existe."""
        url = reverse("admin:index")
        self.assertEqual(url, "/admin/")

    def test_home_url_exists(self):
        """Testa se a URL home existe (mesmo que retorne 404)."""
        # Vamos apenas verificar se não há erro de configuração de URL
        try:
            response = self.client.get("/")
            # Aceita tanto 200 (se a view existir) quanto 404 (se não existir)
            self.assertIn(response.status_code, [200, 404])
        except Exception as e:
            # Se der erro de configuração de URL, falha o teste
            self.fail(f"Erro de configuração de URL: {e}")


@pytest.mark.django_db()
def test_pytest_working():
    """Teste simples usando pytest para verificar se está funcionando."""
    assert True


@pytest.mark.django_db()
def test_user_creation_with_pytest():
    """Teste de criação de usuário usando pytest."""
    user = User.objects.create_user(username="pytest_user", email="pytest@neocargo.com", password="pytest123")

    assert user.username == "pytest_user"
    assert user.email == "pytest@neocargo.com"
    assert user.check_password("pytest123")


def test_math_operations():
    """Teste matemático simples para garantir que o pytest básico funciona."""
    assert 2 + 2 == 4
    assert 10 * 5 == 50
    assert 100 / 4 == 25.0


def test_string_operations():
    """Teste de operações com strings."""
    test_string = "NeoCargo"

    assert len(test_string) == 8
    assert test_string.lower() == "neocargo"
    assert "Neo" in test_string
