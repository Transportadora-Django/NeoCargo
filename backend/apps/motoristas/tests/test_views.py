"""Testes para as views do app motoristas."""

import pytest
from django.urls import reverse

from apps.contas.models import Profile, Role
from apps.motoristas.models import (
    AtribuicaoPedido,
    CategoriaCNH,
    Motorista,
    ProblemaEntrega,
    StatusAtribuicao,
    StatusProblema,
    TipoProblema,
)
from apps.pedidos.models import Pedido, StatusPedido
from apps.rotas.models import Cidade
from apps.veiculos.models import EspecificacaoVeiculo, TipoCombustivel, TipoVeiculo, Veiculo


@pytest.mark.django_db
class TestDashboardMotorista:
    """Testes para a dashboard do motorista."""

    @pytest.fixture
    def setup_motorista(self, django_user_model, client):
        """Configura motorista e faz login."""
        # Criar cidade
        cidade = Cidade.objects.create(nome="São Paulo", estado="SP", latitude=-23.5505, longitude=-46.6333)

        # Criar motorista
        user = django_user_model.objects.create_user(username="motorista_test", password="senha123")
        profile = Profile.objects.get(user=user)
        profile.role = Role.MOTORISTA
        profile.save()
        motorista = Motorista.objects.create(
            profile=profile, sede_atual=cidade, cnh_categoria=CategoriaCNH.D, entregas_concluidas=10
        )

        # Fazer login
        client.login(username="motorista_test", password="senha123")

        return {"motorista": motorista, "cidade": cidade, "user": user}

    def test_dashboard_acesso_motorista(self, client, setup_motorista):
        """Testa que motorista pode acessar dashboard."""
        response = client.get(reverse("motoristas:dashboard"))
        assert response.status_code == 200
        assert "Dashboard do Motorista" in str(response.content)

    def test_dashboard_redirect_nao_autenticado(self, client):
        """Testa redirecionamento para login se não autenticado."""
        response = client.get(reverse("motoristas:dashboard"))
        assert response.status_code == 302
        assert "/contas/login" in response.url

    def test_dashboard_redirect_nao_motorista(self, client, django_user_model):
        """Testa que não-motoristas não acessam dashboard."""
        user = django_user_model.objects.create_user(username="cliente", password="senha123")
        profile = Profile.objects.get(user=user)
        profile.role = Role.CLIENTE
        profile.save()

        client.login(username="cliente", password="senha123")
        response = client.get(reverse("motoristas:dashboard"))
        assert response.status_code == 302

    def test_dashboard_exibe_estatisticas(self, client, setup_motorista):
        """Testa que dashboard exibe estatísticas corretas."""
        response = client.get(reverse("motoristas:dashboard"))
        assert response.status_code == 200
        assert response.context["total_entregas"] == 10
        assert response.context["motorista"] == setup_motorista["motorista"]


@pytest.mark.django_db
class TestRelatarProblema:
    """Testes para relatar problema."""

    @pytest.fixture
    def setup_entrega(self, django_user_model, client):
        """Configura entrega em andamento."""
        cidade = Cidade.objects.create(nome="Rio", estado="RJ", latitude=-22.9, longitude=-43.2)

        # Motorista
        user_motorista = django_user_model.objects.create_user(username="motorista", password="senha123")
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(profile=profile_motorista, sede_atual=cidade, cnh_categoria=CategoriaCNH.C)

        # Veículo
        espec = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.VAN,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=8.0,
            carga_maxima=1500,
            velocidade_media=90,
            reducao_rendimento_principal=0.0005,
        )
        veiculo = Veiculo.objects.create(
            especificacao=espec, marca="Fiat", modelo="Ducato", placa="ABC1234", ano=2020, cor="Branco"
        )

        # Pedido
        user_cliente = django_user_model.objects.create_user(username="cliente", password="senha123")
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Rio",
            cidade_destino="São Paulo",
            peso_carga=500,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )

        # Atribuição
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido, motorista=motorista, veiculo=veiculo, status=StatusAtribuicao.EM_ANDAMENTO
        )

        client.login(username="motorista", password="senha123")

        return {"motorista": motorista, "atribuicao": atribuicao}

    def test_relatar_problema_sucesso(self, client, setup_entrega):
        """Testa relato de problema com sucesso."""
        data = setup_entrega
        url = reverse("motoristas:relatar_problema", kwargs={"atribuicao_id": data["atribuicao"].id})

        response = client.post(url, {"tipo": TipoProblema.VEICULO, "descricao": "Pneu furou"})

        assert response.status_code == 302
        assert ProblemaEntrega.objects.filter(atribuicao=data["atribuicao"]).exists()

        problema = ProblemaEntrega.objects.get(atribuicao=data["atribuicao"])
        assert problema.tipo == TipoProblema.VEICULO
        assert problema.descricao == "Pneu furou"
        assert problema.status == StatusProblema.PENDENTE

    def test_relatar_problema_sem_descricao(self, client, setup_entrega):
        """Testa erro ao relatar problema sem descrição."""
        data = setup_entrega
        url = reverse("motoristas:relatar_problema", kwargs={"atribuicao_id": data["atribuicao"].id})

        response = client.post(url, {"tipo": TipoProblema.VEICULO, "descricao": ""})

        assert response.status_code == 302
        assert not ProblemaEntrega.objects.filter(atribuicao=data["atribuicao"]).exists()

    def test_relatar_problema_entrega_concluida(self, client, setup_entrega):
        """Testa que não pode relatar problema em entrega concluída."""
        data = setup_entrega
        data["atribuicao"].status = StatusAtribuicao.CONCLUIDO
        data["atribuicao"].save()

        url = reverse("motoristas:relatar_problema", kwargs={"atribuicao_id": data["atribuicao"].id})
        response = client.post(url, {"tipo": TipoProblema.VEICULO, "descricao": "Problema"})

        assert response.status_code == 302
        assert not ProblemaEntrega.objects.filter(atribuicao=data["atribuicao"]).exists()


@pytest.mark.django_db
class TestMeusProblemas:
    """Testes para listagem de problemas do motorista."""

    @pytest.fixture
    def setup_problemas(self, django_user_model, client):
        """Configura problemas para teste."""
        cidade = Cidade.objects.create(nome="Curitiba", estado="PR", latitude=-25.4, longitude=-49.2)

        # Motorista
        user_motorista = django_user_model.objects.create_user(username="motorista", password="senha123")
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(profile=profile_motorista, sede_atual=cidade, cnh_categoria=CategoriaCNH.D)

        # Veículo
        espec = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRETA,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=3.5,
            carga_maxima=25000,
            velocidade_media=80,
            reducao_rendimento_principal=0.0001,
        )
        veiculo = Veiculo.objects.create(
            especificacao=espec, marca="Scania", modelo="R450", placa="XYZ9876", ano=2021, cor="Branco"
        )

        # Pedido e atribuição
        user_cliente = django_user_model.objects.create_user(username="cliente", password="senha123")
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Curitiba",
            cidade_destino="Porto Alegre",
            peso_carga=2000,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido, motorista=motorista, veiculo=veiculo, status=StatusAtribuicao.EM_ANDAMENTO
        )

        # Criar problemas
        ProblemaEntrega.objects.create(
            atribuicao=atribuicao, tipo=TipoProblema.VEICULO, descricao="Problema 1", status=StatusProblema.PENDENTE
        )
        ProblemaEntrega.objects.create(
            atribuicao=atribuicao, tipo=TipoProblema.ROTA, descricao="Problema 2", status=StatusProblema.RESOLVIDO
        )

        client.login(username="motorista", password="senha123")

        return {"motorista": motorista}

    def test_listar_problemas(self, client, setup_problemas):
        """Testa listagem de problemas do motorista."""
        response = client.get(reverse("motoristas:meus_problemas"))
        assert response.status_code == 200
        assert response.context["page_obj"].paginator.count == 2

    def test_filtrar_problemas_por_status(self, client, setup_problemas):
        """Testa filtro de problemas por status."""
        response = client.get(reverse("motoristas:meus_problemas") + "?status=pendente")
        assert response.status_code == 200
        assert response.context["page_obj"].paginator.count == 1


@pytest.mark.django_db
class TestConcluirEntrega:
    """Testes para conclusão de entrega."""

    @pytest.fixture
    def setup_entrega_para_concluir(self, django_user_model, client):
        """Configura entrega para conclusão."""
        origem = Cidade.objects.create(nome="Origem", estado="SP", latitude=-23.5, longitude=-46.6)
        destino = Cidade.objects.create(nome="Destino", estado="RJ", latitude=-22.9, longitude=-43.2)

        # Motorista
        user_motorista = django_user_model.objects.create_user(username="motorista", password="senha123")
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=origem,
            cnh_categoria=CategoriaCNH.C,
            disponivel=False,
            entregas_concluidas=5,
        )

        # Veículo
        espec = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.VAN,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=8.0,
            carga_maxima=1500,
            velocidade_media=90,
            reducao_rendimento_principal=0.0005,
        )
        veiculo = Veiculo.objects.create(
            especificacao=espec,
            marca="Mercedes",
            modelo="Sprinter",
            placa="DEF5678",
            ano=2019,
            cor="Branco",
            sede_atual=origem,
        )

        # Pedido
        user_cliente = django_user_model.objects.create_user(username="cliente", password="senha123")
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Origem",
            cidade_destino="Destino",
            peso_carga=1000,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )

        # Atribuição
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido, motorista=motorista, veiculo=veiculo, status=StatusAtribuicao.EM_ANDAMENTO
        )

        client.login(username="motorista", password="senha123")

        return {"motorista": motorista, "atribuicao": atribuicao, "destino": destino}

    def test_concluir_entrega_sucesso(self, client, setup_entrega_para_concluir):
        """Testa conclusão de entrega com sucesso."""
        data = setup_entrega_para_concluir
        url = reverse("motoristas:concluir_entrega", kwargs={"atribuicao_id": data["atribuicao"].id})

        response = client.post(url)

        assert response.status_code == 302

        # Verificar mudanças
        data["atribuicao"].refresh_from_db()
        data["motorista"].refresh_from_db()

        assert data["atribuicao"].status == StatusAtribuicao.CONCLUIDO
        assert data["motorista"].disponivel is True
        assert data["motorista"].entregas_concluidas == 6
        assert data["motorista"].sede_atual == data["destino"]

    def test_concluir_entrega_nao_em_andamento(self, client, setup_entrega_para_concluir):
        """Testa erro ao tentar concluir entrega que não está em andamento."""
        data = setup_entrega_para_concluir
        data["atribuicao"].status = StatusAtribuicao.PENDENTE
        data["atribuicao"].save()

        url = reverse("motoristas:concluir_entrega", kwargs={"atribuicao_id": data["atribuicao"].id})
        response = client.post(url)

        assert response.status_code == 302
        data["atribuicao"].refresh_from_db()
        assert data["atribuicao"].status == StatusAtribuicao.PENDENTE  # Não mudou
