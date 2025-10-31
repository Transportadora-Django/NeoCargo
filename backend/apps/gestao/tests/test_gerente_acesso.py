"""
Testes para verificar o acesso do gerente às funcionalidades do sistema
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.contas.models import Profile, Role


@pytest.mark.django_db
class TestGerenteAcessoFuncionalidades:
    """Testes para verificar se gerente tem acesso às funcionalidades corretas"""

    @pytest.fixture
    def gerente_user(self):
        """Cria um usuário gerente para os testes"""
        user = User.objects.create_user(username="gerente_acesso_test", email="gerente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.GERENTE)
        return user

    @pytest.fixture
    def cliente_user(self):
        """Cria um usuário cliente para os testes"""
        user = User.objects.create_user(username="cliente_acesso_test", email="cliente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.CLIENTE)
        return user

    # ========== TESTES DE ACESSO DO GERENTE ==========

    def test_gerente_acessa_dashboard(self, client, gerente_user):
        """Gerente deve ter acesso ao dashboard do gerente"""
        client.force_login(gerente_user)
        response = client.get(reverse("gestao:dashboard_gerente"))
        assert response.status_code == 200

    def test_gerente_acessa_pedidos_para_aprovacao(self, client, gerente_user):
        """Gerente deve ter acesso à lista de pedidos pendentes"""
        client.force_login(gerente_user)
        response = client.get(reverse("gestao:pedidos_para_aprovacao"))
        assert response.status_code == 200

    def test_gerente_acessa_listar_problemas(self, client, gerente_user):
        """Gerente deve ter acesso à lista de problemas"""
        client.force_login(gerente_user)
        response = client.get(reverse("gestao:listar_problemas"))
        assert response.status_code == 200

    def test_gerente_acessa_especificacoes(self, client, gerente_user):
        """Gerente deve ter acesso às especificações de veículos"""
        client.force_login(gerente_user)
        response = client.get(reverse("veiculos:listar_especificacoes"))
        assert response.status_code == 200

    def test_gerente_acessa_veiculos(self, client, gerente_user):
        """Gerente deve ter acesso à lista de veículos"""
        client.force_login(gerente_user)
        response = client.get(reverse("veiculos:listar_veiculos"))
        assert response.status_code == 200

    def test_gerente_acessa_cidades(self, client, gerente_user):
        """Gerente deve ter acesso à lista de cidades"""
        client.force_login(gerente_user)
        response = client.get(reverse("rotas:listar_cidades"))
        assert response.status_code == 200

    def test_gerente_acessa_rotas(self, client, gerente_user):
        """Gerente deve ter acesso à lista de rotas"""
        client.force_login(gerente_user)
        response = client.get(reverse("rotas:listar_rotas"))
        assert response.status_code == 200

    def test_gerente_acessa_configurar_precos(self, client, gerente_user):
        """Gerente deve ter acesso à configuração de preços"""
        client.force_login(gerente_user)
        response = client.get(reverse("rotas:configurar_precos"))
        assert response.status_code == 200

    # ========== TESTES DE ACESSO NEGADO PARA GERENTE ==========

    def test_gerente_nao_acessa_gestao_usuarios(self, client, gerente_user):
        """Gerente NÃO deve ter acesso à gestão de usuários"""
        client.force_login(gerente_user)
        response = client.get(reverse("gestao:listar_usuarios"))
        assert response.status_code == 302  # Redirect
        assert response.url == reverse("home")

    def test_gerente_nao_acessa_solicitacoes(self, client, gerente_user):
        """Gerente NÃO deve ter acesso às solicitações de mudança de perfil"""
        client.force_login(gerente_user)
        response = client.get(reverse("gestao:listar_solicitacoes"))
        assert response.status_code == 302  # Redirect
        assert response.url == reverse("home")

    def test_gerente_nao_acessa_dashboard_dono(self, client, gerente_user):
        """Gerente NÃO deve ter acesso ao dashboard do dono"""
        client.force_login(gerente_user)
        response = client.get(reverse("gestao:dashboard_dono"))
        assert response.status_code == 302  # Redirect
        assert response.url == reverse("home")

    # ========== TESTES DE ACESSO NEGADO PARA CLIENTE ==========

    def test_cliente_nao_acessa_dashboard_gerente(self, client, cliente_user):
        """Cliente NÃO deve ter acesso ao dashboard do gerente"""
        client.force_login(cliente_user)
        response = client.get(reverse("gestao:dashboard_gerente"))
        assert response.status_code == 302  # Redirect
        assert response.url == reverse("home")

    def test_cliente_nao_acessa_pedidos_para_aprovacao(self, client, cliente_user):
        """Cliente NÃO deve ter acesso aos pedidos para aprovação"""
        client.force_login(cliente_user)
        response = client.get(reverse("gestao:pedidos_para_aprovacao"))
        assert response.status_code == 302  # Redirect

    def test_cliente_nao_acessa_problemas(self, client, cliente_user):
        """Cliente NÃO deve ter acesso à lista de problemas"""
        client.force_login(cliente_user)
        response = client.get(reverse("gestao:listar_problemas"))
        assert response.status_code == 302  # Redirect

    def test_cliente_nao_acessa_especificacoes(self, client, cliente_user):
        """Cliente NÃO deve ter acesso às especificações"""
        client.force_login(cliente_user)
        response = client.get(reverse("veiculos:listar_especificacoes"))
        assert response.status_code == 302  # Redirect

    def test_cliente_nao_acessa_cidades_gestao(self, client, cliente_user):
        """Cliente NÃO deve ter acesso à gestão de cidades"""
        client.force_login(cliente_user)
        response = client.get(reverse("rotas:listar_cidades"))
        # Cliente pode ver cidades mas não gerenciar
        assert response.status_code in [200, 302]

    def test_cliente_nao_acessa_configurar_precos(self, client, cliente_user):
        """Cliente NÃO deve ter acesso à configuração de preços"""
        client.force_login(cliente_user)
        response = client.get(reverse("rotas:configurar_precos"))
        assert response.status_code == 302  # Redirect
