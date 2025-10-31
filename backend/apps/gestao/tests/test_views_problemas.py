"""Testes para views de gestão de problemas."""

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
class TestListarProblemas:
    """Testes para listagem de problemas por owner/gerente."""

    @pytest.fixture
    def setup_problemas_gestao(self, django_user_model, client):
        """Configura problemas para testes de gestão."""
        cidade = Cidade.objects.create(nome="São Paulo", estado="SP", latitude=-23.5, longitude=-46.6)

        # Owner
        user_owner = django_user_model.objects.create_user(username="owner", password="senha123")
        profile_owner = Profile.objects.get(user=user_owner)
        profile_owner.role = Role.OWNER
        profile_owner.save()

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
            especificacao=espec, marca="Scania", modelo="R450", placa="ABC1234", ano=2021, cor="Branco"
        )

        # Cliente e pedido
        user_cliente = django_user_model.objects.create_user(username="cliente", password="senha123")
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=2000,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )

        # Atribuição
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido, motorista=motorista, veiculo=veiculo, status=StatusAtribuicao.EM_ANDAMENTO
        )

        # Criar problemas
        problema1 = ProblemaEntrega.objects.create(
            atribuicao=atribuicao,
            tipo=TipoProblema.VEICULO,
            descricao="Pneu furou",
            status=StatusProblema.PENDENTE,
        )
        problema2 = ProblemaEntrega.objects.create(
            atribuicao=atribuicao,
            tipo=TipoProblema.ROTA,
            descricao="Estrada interditada",
            status=StatusProblema.EM_ANALISE,
        )
        problema3 = ProblemaEntrega.objects.create(
            atribuicao=atribuicao,
            tipo=TipoProblema.ACIDENTE,
            descricao="Acidente leve",
            status=StatusProblema.RESOLVIDO,
            resolucao="Resolvido",
        )

        client.login(username="owner", password="senha123")

        return {
            "problema1": problema1,
            "problema2": problema2,
            "problema3": problema3,
        }

    def test_listar_problemas_owner(self, client, setup_problemas_gestao):
        """Testa que owner pode acessar listagem de problemas."""
        response = client.get(reverse("gestao:listar_problemas"))
        assert response.status_code == 200
        assert "Problemas Reportados" in str(response.content)

    def test_listar_problemas_exclui_resolvidos_por_padrao(self, client, setup_problemas_gestao):
        """Testa que por padrão não mostra problemas resolvidos."""
        response = client.get(reverse("gestao:listar_problemas"))
        assert response.status_code == 200
        # Deve mostrar 2 (pendente e em_analise), não 3
        assert response.context["page_obj"].paginator.count == 2

    def test_listar_problemas_filtro_status(self, client, setup_problemas_gestao):
        """Testa filtro por status."""
        response = client.get(reverse("gestao:listar_problemas") + "?status=pendente")
        assert response.status_code == 200
        assert response.context["page_obj"].paginator.count == 1

    def test_listar_problemas_filtro_tipo(self, client, setup_problemas_gestao):
        """Testa filtro por tipo."""
        response = client.get(reverse("gestao:listar_problemas") + "?tipo=veiculo")
        assert response.status_code == 200
        assert response.context["page_obj"].paginator.count == 1

    def test_listar_problemas_busca(self, client, setup_problemas_gestao):
        """Testa busca por descrição."""
        response = client.get(reverse("gestao:listar_problemas") + "?q=pneu")
        assert response.status_code == 200
        assert response.context["page_obj"].paginator.count == 1

    def test_listar_problemas_acesso_negado_cliente(self, client, django_user_model):
        """Testa que cliente não pode acessar listagem."""
        user_cliente = django_user_model.objects.create_user(username="cliente_test", password="senha123")
        profile = Profile.objects.get(user=user_cliente)
        profile.role = Role.CLIENTE
        profile.save()

        client.login(username="cliente_test", password="senha123")
        response = client.get(reverse("gestao:listar_problemas"))
        assert response.status_code == 302  # Redirect


@pytest.mark.django_db
class TestAnalisarProblema:
    """Testes para marcar problema como em análise."""

    @pytest.fixture
    def setup_problema_pendente(self, django_user_model, client):
        """Configura problema pendente."""
        cidade = Cidade.objects.create(nome="Curitiba", estado="PR", latitude=-25.4, longitude=-49.2)

        # Gerente
        user_gerente = django_user_model.objects.create_user(username="gerente", password="senha123")
        profile_gerente = Profile.objects.get(user=user_gerente)
        profile_gerente.role = Role.GERENTE
        profile_gerente.save()

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
            especificacao=espec, marca="Fiat", modelo="Ducato", placa="XYZ9876", ano=2020, cor="Branco"
        )

        # Pedido
        user_cliente = django_user_model.objects.create_user(username="cliente", password="senha123")
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Curitiba",
            cidade_destino="Porto Alegre",
            peso_carga=1000,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )

        # Atribuição e problema
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido, motorista=motorista, veiculo=veiculo, status=StatusAtribuicao.EM_ANDAMENTO
        )
        problema = ProblemaEntrega.objects.create(
            atribuicao=atribuicao, tipo=TipoProblema.CARGA, descricao="Carga danificada", status=StatusProblema.PENDENTE
        )

        client.login(username="gerente", password="senha123")

        return {"problema": problema}

    def test_analisar_problema_sucesso(self, client, setup_problema_pendente):
        """Testa marcação de problema como em análise."""
        data = setup_problema_pendente
        url = reverse("gestao:analisar_problema", kwargs={"problema_id": data["problema"].id})

        response = client.post(url)

        assert response.status_code == 302
        data["problema"].refresh_from_db()
        assert data["problema"].status == StatusProblema.EM_ANALISE

    def test_analisar_problema_ja_resolvido(self, client, setup_problema_pendente):
        """Testa erro ao tentar analisar problema já resolvido."""
        data = setup_problema_pendente
        data["problema"].status = StatusProblema.RESOLVIDO
        data["problema"].save()

        url = reverse("gestao:analisar_problema", kwargs={"problema_id": data["problema"].id})
        response = client.post(url)

        assert response.status_code == 302
        # Status não deve mudar
        data["problema"].refresh_from_db()
        assert data["problema"].status == StatusProblema.RESOLVIDO


@pytest.mark.django_db
class TestResolverProblema:
    """Testes para resolver problema."""

    @pytest.fixture
    def setup_problema_analise(self, django_user_model, client):
        """Configura problema em análise."""
        cidade = Cidade.objects.create(nome="Porto Alegre", estado="RS", latitude=-30.0, longitude=-51.2)

        # Owner
        user_owner = django_user_model.objects.create_user(username="owner", password="senha123")
        profile_owner = Profile.objects.get(user=user_owner)
        profile_owner.role = Role.OWNER
        profile_owner.save()

        # Motorista
        user_motorista = django_user_model.objects.create_user(username="motorista", password="senha123")
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(profile=profile_motorista, sede_atual=cidade, cnh_categoria=CategoriaCNH.E)

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
            especificacao=espec, marca="Mercedes", modelo="Actros", placa="DEF5678", ano=2019, cor="Branco"
        )

        # Pedido
        user_cliente = django_user_model.objects.create_user(username="cliente", password="senha123")
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Porto Alegre",
            cidade_destino="Florianópolis",
            peso_carga=3000,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )

        # Atribuição e problema
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido,
            motorista=motorista,
            veiculo=veiculo,
            status=StatusAtribuicao.EM_ANDAMENTO,
        )
        problema = ProblemaEntrega.objects.create(
            atribuicao=atribuicao,
            tipo=TipoProblema.OUTRO,
            descricao="Problema diverso",
            status=StatusProblema.EM_ANALISE,
        )

        client.login(username="owner", password="senha123")

        return {"problema": problema}

    def test_resolver_problema_sucesso(self, client, setup_problema_analise):
        """Testa resolução de problema com sucesso."""
        data = setup_problema_analise
        url = reverse("gestao:resolver_problema", kwargs={"problema_id": data["problema"].id})

        response = client.post(url, {"resolucao": "Problema resolvido com troca de peça"})

        assert response.status_code == 302
        data["problema"].refresh_from_db()
        assert data["problema"].status == StatusProblema.RESOLVIDO
        assert data["problema"].resolucao == "Problema resolvido com troca de peça"
        assert data["problema"].resolvido_em is not None

    def test_resolver_problema_sem_resolucao(self, client, setup_problema_analise):
        """Testa erro ao tentar resolver sem descrição."""
        data = setup_problema_analise
        url = reverse("gestao:resolver_problema", kwargs={"problema_id": data["problema"].id})

        response = client.post(url, {"resolucao": ""})

        assert response.status_code == 302
        data["problema"].refresh_from_db()
        assert data["problema"].status == StatusProblema.EM_ANALISE  # Não mudou

    def test_resolver_problema_ja_resolvido(self, client, setup_problema_analise):
        """Testa erro ao tentar resolver problema já resolvido."""
        data = setup_problema_analise
        data["problema"].status = StatusProblema.RESOLVIDO
        data["problema"].resolucao = "Já resolvido"
        data["problema"].save()

        url = reverse("gestao:resolver_problema", kwargs={"problema_id": data["problema"].id})
        response = client.post(url, {"resolucao": "Nova resolução"})

        assert response.status_code == 302
        data["problema"].refresh_from_db()
        assert data["problema"].resolucao == "Já resolvido"  # Não mudou
