"""
Testes para o alerta de problemas no dashboard do dono e gerente
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.contas.models import Profile, Role
from apps.motoristas.models import Motorista, ProblemaEntrega, StatusProblema, TipoProblema, AtribuicaoPedido
from apps.pedidos.models import Pedido, StatusPedido, OpcaoCotacao
from apps.veiculos.models import Veiculo, EspecificacaoVeiculo, TipoVeiculo, TipoCombustivel
from apps.rotas.models import Cidade, Estado
from decimal import Decimal


@pytest.mark.django_db
class TestAlertaProblemasDashboard:
    """Testes para o alerta de problemas no dashboard"""

    @pytest.fixture
    def dono_user(self):
        """Cria um usuário dono"""
        user = User.objects.create_user(username="dono_test", email="dono@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.OWNER)
        return user

    @pytest.fixture
    def gerente_user(self):
        """Cria um usuário gerente"""
        user = User.objects.create_user(username="gerente_test", email="gerente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.GERENTE)
        return user

    @pytest.fixture
    def cliente_user(self):
        """Cria um usuário cliente"""
        user = User.objects.create_user(username="cliente_test", email="cliente@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        Profile.objects.create(user=user, role=Role.CLIENTE)
        return user

    @pytest.fixture
    def motorista_user(self):
        """Cria um usuário motorista"""
        user = User.objects.create_user(username="motorista_test", email="motorista@test.com", password="senha123")
        Profile.objects.filter(user=user).delete()
        profile = Profile.objects.create(user=user, role=Role.MOTORISTA)
        return user, profile

    @pytest.fixture
    def cidade(self):
        """Cria uma cidade para testes"""
        return Cidade.objects.create(nome="Test City", estado=Estado.SP, latitude=0, longitude=0)

    @pytest.fixture
    def especificacao(self):
        """Especificação de veículo"""
        return EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRETA,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=3.5,
            carga_maxima=10000.00,
            velocidade_media=80,
            reducao_rendimento_principal=0.0001,
        )

    @pytest.fixture
    def veiculo(self, especificacao):
        """Cria um veículo para testes"""
        return Veiculo.objects.create(
            especificacao=especificacao,
            marca="Ford",
            modelo="Transit",
            placa="ABC1234",
            ano=2020,
            cor="Branco",
            ativo=True,
        )

    @pytest.fixture
    def motorista(self, motorista_user, cidade):
        """Cria um motorista"""
        user, profile = motorista_user
        return Motorista.objects.create(profile=profile, sede_atual=cidade, cnh_categoria="D")

    @pytest.fixture
    def pedido(self, cliente_user):
        """Cria um pedido em transporte"""
        return Pedido.objects.create(
            cliente=cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("1000"),
            prazo_desejado=5,
            opcao=OpcaoCotacao.ECONOMICO,
            status=StatusPedido.EM_TRANSPORTE,
        )

    @pytest.fixture
    def atribuicao(self, pedido, motorista, veiculo):
        """Cria uma atribuição"""
        return AtribuicaoPedido.objects.create(pedido=pedido, motorista=motorista, veiculo=veiculo)

    @pytest.fixture
    def problema_pendente(self, atribuicao):
        """Cria um problema pendente"""
        return ProblemaEntrega.objects.create(
            atribuicao=atribuicao,
            tipo=TipoProblema.VEICULO,
            descricao="Problema mecânico",
            status=StatusProblema.PENDENTE,
        )

    @pytest.fixture
    def problema_em_analise(self, atribuicao):
        """Cria um problema em análise"""
        return ProblemaEntrega.objects.create(
            atribuicao=atribuicao,
            tipo=TipoProblema.CARGA,
            descricao="Dano na carga",
            status=StatusProblema.EM_ANALISE,
        )

    def test_dashboard_dono_mostra_alerta_com_problemas_pendentes(
        self, client, dono_user, problema_pendente
    ):
        """Testa se dashboard do dono mostra alerta quando há problemas pendentes"""
        client.force_login(dono_user)
        url = reverse("gestao:dashboard_dono")
        response = client.get(url)

        assert response.status_code == 200
        assert "Problemas Reportados" in response.content.decode()
        assert "1 pendente" in response.content.decode() or "pendente" in response.content.decode()

    def test_dashboard_dono_mostra_alerta_com_problemas_em_analise(
        self, client, dono_user, problema_em_analise
    ):
        """Testa se dashboard do dono mostra alerta quando há problemas em análise"""
        client.force_login(dono_user)
        url = reverse("gestao:dashboard_dono")
        response = client.get(url)

        assert response.status_code == 200
        assert "Problemas Reportados" in response.content.decode()
        assert "em análise" in response.content.decode()

    def test_dashboard_dono_nao_mostra_alerta_sem_problemas(self, client, dono_user):
        """Testa se dashboard do dono não mostra alerta quando não há problemas"""
        client.force_login(dono_user)
        url = reverse("gestao:dashboard_dono")
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        # Não deve aparecer o card de problemas se não houver problemas
        assert response.context["total_problemas_pendentes"] == 0
        assert response.context["total_problemas_em_analise"] == 0

    def test_dashboard_gerente_mostra_alerta_com_problemas(self, client, gerente_user, problema_pendente):
        """Testa se dashboard do gerente mostra alerta quando há problemas"""
        client.force_login(gerente_user)
        url = reverse("gestao:dashboard_gerente")
        response = client.get(url)

        assert response.status_code == 200
        assert "Problemas Reportados" in response.content.decode()

    def test_dashboard_gerente_conta_problemas_corretamente(
        self, client, gerente_user, problema_pendente, problema_em_analise
    ):
        """Testa se dashboard do gerente conta problemas corretamente"""
        client.force_login(gerente_user)
        url = reverse("gestao:dashboard_gerente")
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["total_problemas_pendentes"] == 1
        assert response.context["total_problemas_em_analise"] == 1

    def test_dashboard_dono_tem_botao_ver_problemas(self, client, dono_user, problema_pendente):
        """Testa se dashboard do dono tem botão para ver problemas"""
        client.force_login(dono_user)
        url = reverse("gestao:dashboard_dono")
        response = client.get(url)

        assert response.status_code == 200
        assert "Ver Problemas" in response.content.decode()
        assert reverse("gestao:listar_problemas") in response.content.decode()
