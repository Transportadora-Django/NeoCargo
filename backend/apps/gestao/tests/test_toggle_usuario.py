"""
Testes para a funcionalidade de ativar/desativar usuários (NC-36)
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.contas.models import Profile, Role


@pytest.mark.django_db
class TestToggleUsuarioStatus:
    """Testes para a view toggle_usuario_status"""

    @pytest.fixture
    def dono_user(self):
        """Cria um usuário dono para os testes"""
        user = User.objects.create_user(username="dono_test", email="dono@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.OWNER)
        return user

    @pytest.fixture
    def cliente_user(self):
        """Cria um usuário cliente para os testes"""
        user = User.objects.create_user(username="cliente_test", email="cliente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.CLIENTE)
        return user

    @pytest.fixture
    def motorista_user(self):
        """Cria um usuário motorista para os testes"""
        user = User.objects.create_user(username="motorista_test", email="motorista@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.MOTORISTA)
        return user

    @pytest.fixture
    def gerente_user(self):
        """Cria um usuário gerente para os testes"""
        user = User.objects.create_user(username="gerente_test", email="gerente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.GERENTE)
        return user

    def test_dono_pode_desativar_cliente(self, client, dono_user, cliente_user):
        """Testa se dono pode desativar um cliente"""
        client.force_login(dono_user)
        assert cliente_user.is_active is True

        url = reverse("gestao:toggle_usuario_status", args=[cliente_user.id])
        response = client.post(url)

        assert response.status_code == 302
        cliente_user.refresh_from_db()
        assert cliente_user.is_active is False

    def test_dono_pode_reativar_cliente(self, client, dono_user, cliente_user):
        """Testa se dono pode reativar um cliente desativado"""
        cliente_user.is_active = False
        cliente_user.save()

        client.force_login(dono_user)
        url = reverse("gestao:toggle_usuario_status", args=[cliente_user.id])
        response = client.post(url)

        assert response.status_code == 302
        cliente_user.refresh_from_db()
        assert cliente_user.is_active is True

    def test_dono_nao_pode_desativar_proprio_usuario(self, client, dono_user):
        """Testa se dono não pode desativar sua própria conta"""
        client.force_login(dono_user)

        url = reverse("gestao:toggle_usuario_status", args=[dono_user.id])
        response = client.post(url)

        assert response.status_code == 302
        dono_user.refresh_from_db()
        assert dono_user.is_active is True  # Deve continuar ativo

    def test_dono_nao_pode_desativar_outro_dono(self, client, dono_user):
        """Testa se dono não pode desativar outro dono"""
        outro_dono = User.objects.create_user(username="outro_dono", email="outro@test.com", password="senha123")
        Profile.objects.filter(user=outro_dono).delete()
        Profile.objects.create(user=outro_dono, role=Role.OWNER)

        client.force_login(dono_user)
        url = reverse("gestao:toggle_usuario_status", args=[outro_dono.id])
        response = client.post(url)

        assert response.status_code == 302
        outro_dono.refresh_from_db()
        assert outro_dono.is_active is True  # Deve continuar ativo

    def test_gerente_nao_pode_desativar_usuario(self, client, gerente_user, cliente_user):
        """Testa se gerente não pode desativar usuários"""
        client.force_login(gerente_user)

        url = reverse("gestao:toggle_usuario_status", args=[cliente_user.id])
        response = client.post(url)

        assert response.status_code == 302  # Redirect para home ou mensagem de erro

    def test_cliente_nao_pode_desativar_usuario(self, client, cliente_user, motorista_user):
        """Testa se cliente não pode desativar usuários"""
        client.force_login(cliente_user)

        url = reverse("gestao:toggle_usuario_status", args=[motorista_user.id])
        response = client.post(url)

        assert response.status_code == 302  # Redirect para home ou mensagem de erro

    def test_dono_pode_desativar_motorista(self, client, dono_user, motorista_user):
        """Testa se dono pode desativar um motorista"""
        client.force_login(dono_user)
        assert motorista_user.is_active is True

        url = reverse("gestao:toggle_usuario_status", args=[motorista_user.id])
        response = client.post(url)

        assert response.status_code == 302
        motorista_user.refresh_from_db()
        assert motorista_user.is_active is False

    def test_dono_pode_desativar_gerente(self, client, dono_user, gerente_user):
        """Testa se dono pode desativar um gerente"""
        client.force_login(dono_user)
        assert gerente_user.is_active is True

        url = reverse("gestao:toggle_usuario_status", args=[gerente_user.id])
        response = client.post(url)

        assert response.status_code == 302
        gerente_user.refresh_from_db()
        assert gerente_user.is_active is False
