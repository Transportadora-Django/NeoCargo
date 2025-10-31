"""
Testes para o dashboard do gerente
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.contas.models import Profile, Role
from apps.rotas.models import Cidade, Estado


@pytest.mark.django_db
class TestDashboardGerente:
    """Testes para a view dashboard_gerente"""

    @pytest.fixture
    def gerente_user(self):
        """Cria um usuário gerente para os testes"""
        user = User.objects.create_user(username="gerente_test", email="gerente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.GERENTE)
        return user

    @pytest.fixture
    def cliente_user(self):
        """Cria um usuário cliente para os testes"""
        user = User.objects.create_user(username="cliente_test", email="cliente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.CLIENTE)
        return user

    def test_dashboard_gerente_acesso_autorizado(self, client, gerente_user):
        """Testa se gerente consegue acessar o dashboard"""
        client.force_login(gerente_user)
        url = reverse("gestao:dashboard_gerente")
        response = client.get(url)

        assert response.status_code == 200
        assert "Dashboard do Gerente" in response.content.decode()

    def test_dashboard_gerente_acesso_negado_cliente(self, client, cliente_user):
        """Testa se cliente NÃO consegue acessar o dashboard do gerente"""
        client.force_login(cliente_user)
        url = reverse("gestao:dashboard_gerente")
        response = client.get(url)

        assert response.status_code == 302  # Redirect
        assert response.url == reverse("home")

    def test_dashboard_gerente_sem_autenticacao(self, client):
        """Testa redirecionamento sem autenticação"""
        url = reverse("gestao:dashboard_gerente")
        response = client.get(url)

        assert response.status_code == 302
        assert "/contas/login/" in response.url

    def test_dashboard_gerente_estatisticas(self, client, gerente_user):
        """Testa se as estatísticas são exibidas corretamente"""
        client.force_login(gerente_user)

        # Criar dados de teste
        Cidade.objects.create(nome="Test City", estado=Estado.SP, latitude=0, longitude=0)

        url = reverse("gestao:dashboard_gerente")
        response = client.get(url)

        assert response.status_code == 200
        context = response.context

        # Verificar que as estatísticas estão no contexto
        assert "total_clientes" in context
        assert "total_motoristas" in context
        assert "total_veiculos" in context
        assert "total_pedidos" in context
        assert "pedidos_pendentes" in context
        assert "total_problemas_pendentes" in context
        assert "problemas_recentes" in context

    def test_dashboard_gerente_nao_mostra_gestao_usuarios(self, client, gerente_user):
        """Testa que o dashboard do gerente NÃO mostra dados de gestão de usuários"""
        client.force_login(gerente_user)
        url = reverse("gestao:dashboard_gerente")
        response = client.get(url)

        assert response.status_code == 200
        context = response.context

        # Verificar que NÃO tem estatísticas de usuários totais e solicitações
        assert "total_usuarios" not in context
        assert "total_solicitacoes_pendentes" not in context
        assert "usuarios_recentes" not in context
        assert "solicitacoes_recentes" not in context
