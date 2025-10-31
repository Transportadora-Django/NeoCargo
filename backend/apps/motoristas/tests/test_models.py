"""Testes para os modelos do app motoristas."""

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone

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
class TestMotorista:
    """Testes para o modelo Motorista."""

    @pytest.fixture
    def cidade(self):
        """Cria uma cidade de teste."""
        return Cidade.objects.create(
            nome="São Paulo",
            estado="SP",
            latitude=-23.5505,
            longitude=-46.6333,
        )

    @pytest.fixture
    def profile_motorista(self, django_user_model, cidade):
        """Cria um profile de motorista."""
        user = django_user_model.objects.create_user(
            username="motorista_test",
            email="motorista@test.com",
            password="senha123",
        )
        profile = Profile.objects.get(user=user)
        profile.role = Role.MOTORISTA
        profile.save()
        return profile

    def test_criar_motorista_sucesso(self, profile_motorista, cidade):
        """Testa criação de motorista com dados válidos."""
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.C,
            disponivel=True,
            entregas_concluidas=0,
        )

        assert motorista.id is not None
        assert motorista.profile == profile_motorista
        assert motorista.sede_atual == cidade
        assert motorista.cnh_categoria == CategoriaCNH.C
        assert motorista.disponivel is True
        assert motorista.entregas_concluidas == 0

    def test_motorista_str(self, profile_motorista, cidade):
        """Testa representação em string do motorista."""
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.D,
        )

        assert str(motorista) == "motorista_test - CNH D - São Paulo/SP"

    def test_motorista_unique_profile(self, profile_motorista, cidade):
        """Testa que não pode haver dois motoristas com o mesmo profile."""
        Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.B,
        )

        with pytest.raises(IntegrityError):
            Motorista.objects.create(
                profile=profile_motorista,
                sede_atual=cidade,
                cnh_categoria=CategoriaCNH.C,
            )

    def test_motorista_entregas_concluidas_default(self, profile_motorista, cidade):
        """Testa que entregas_concluidas tem valor padrão 0."""
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.E,
        )

        assert motorista.entregas_concluidas == 0

    def test_motorista_disponivel_default(self, profile_motorista, cidade):
        """Testa que disponivel tem valor padrão True."""
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.B,
        )

        assert motorista.disponivel is True

    def test_categorias_cnh_validas(self):
        """Testa que todas as categorias de CNH estão disponíveis."""
        categorias = [c.value for c in CategoriaCNH]
        assert "B" in categorias
        assert "C" in categorias
        assert "D" in categorias
        assert "E" in categorias


@pytest.mark.django_db
class TestAtribuicaoPedido:
    """Testes para o modelo AtribuicaoPedido."""

    @pytest.fixture
    def setup_atribuicao(self, django_user_model):
        """Configura dados necessários para testes de atribuição."""
        # Criar cidade
        cidade = Cidade.objects.create(
            nome="Rio de Janeiro",
            estado="RJ",
            latitude=-22.9068,
            longitude=-43.1729,
        )

        # Criar cliente
        user_cliente = django_user_model.objects.create_user(
            username="cliente_test",
            email="cliente@test.com",
            password="senha123",
        )
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()

        # Criar motorista
        user_motorista = django_user_model.objects.create_user(
            username="motorista_atrib",
            email="motorista@atrib.com",
            password="senha123",
        )
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.D,
        )

        # Criar veículo
        espec = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRETA,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=3.5,
            carga_maxima=25000,
            velocidade_media=80,
            reducao_rendimento_principal=0.0001,
        )
        veiculo = Veiculo.objects.create(
            especificacao=espec,
            marca="Mercedes",
            modelo="Accelo 1016",
            placa="ABC1234",
            ano=2020,
            cor="Branco",
            sede_atual=cidade,
            categoria_minima_cnh=CategoriaCNH.C,
        )

        # Criar pedido
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Rio de Janeiro",
            cidade_destino="São Paulo",
            peso_carga=1000,
            prazo_desejado=3,
            status=StatusPedido.PENDENTE,
        )

        return {
            "motorista": motorista,
            "veiculo": veiculo,
            "pedido": pedido,
        }

    def test_criar_atribuicao_sucesso(self, setup_atribuicao):
        """Testa criação de atribuição com dados válidos."""
        data = setup_atribuicao
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=data["pedido"],
            motorista=data["motorista"],
            veiculo=data["veiculo"],
            status=StatusAtribuicao.PENDENTE,
        )

        assert atribuicao.id is not None
        assert atribuicao.pedido == data["pedido"]
        assert atribuicao.motorista == data["motorista"]
        assert atribuicao.veiculo == data["veiculo"]
        assert atribuicao.status == StatusAtribuicao.PENDENTE
        assert atribuicao.created_at is not None

    def test_atribuicao_str(self, setup_atribuicao):
        """Testa representação em string da atribuição."""
        data = setup_atribuicao
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=data["pedido"],
            motorista=data["motorista"],
            veiculo=data["veiculo"],
            status=StatusAtribuicao.EM_ANDAMENTO,
        )

        expected = f"Pedido #{data['pedido'].id} - motorista_atrib - ABC1234"
        assert str(atribuicao) == expected

    def test_atribuicao_unique_pedido(self, setup_atribuicao):
        """Testa que não pode haver duas atribuições para o mesmo pedido."""
        data = setup_atribuicao
        AtribuicaoPedido.objects.create(
            pedido=data["pedido"],
            motorista=data["motorista"],
            veiculo=data["veiculo"],
            status=StatusAtribuicao.PENDENTE,
        )

        with pytest.raises(IntegrityError):
            AtribuicaoPedido.objects.create(
                pedido=data["pedido"],
                motorista=data["motorista"],
                veiculo=data["veiculo"],
                status=StatusAtribuicao.PENDENTE,
            )

    def test_status_atribuicao_validos(self):
        """Testa que todos os status de atribuição estão disponíveis."""
        status = [s.value for s in StatusAtribuicao]
        assert "pendente" in status
        assert "em_andamento" in status
        assert "concluido" in status
        assert "cancelado" in status

    def test_atribuicao_status_default(self, setup_atribuicao):
        """Testa que o status padrão é PENDENTE."""
        data = setup_atribuicao
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=data["pedido"],
            motorista=data["motorista"],
            veiculo=data["veiculo"],
        )

        assert atribuicao.status == StatusAtribuicao.PENDENTE


@pytest.mark.django_db
class TestProblemaEntrega:
    """Testes para o modelo ProblemaEntrega."""

    @pytest.fixture
    def setup_problema(self, django_user_model):
        """Configura dados necessários para testes de problema."""
        # Criar cidade
        cidade = Cidade.objects.create(
            nome="Porto Alegre",
            estado="RS",
            latitude=-30.0346,
            longitude=-51.2177,
        )

        # Criar motorista
        user_motorista = django_user_model.objects.create_user(
            username="motorista_problema",
            email="motorista@problema.com",
            password="senha123",
        )
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.C,
        )

        # Criar veículo
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
            marca="Fiat",
            modelo="Ducato",
            placa="XYZ1234",
            ano=2020,
            cor="Branco",
            sede_atual=cidade,
        )

        # Criar cliente e pedido
        user_cliente = django_user_model.objects.create_user(
            username="cliente_problema",
            email="cliente@problema.com",
            password="senha123",
        )
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Porto Alegre",
            cidade_destino="Porto Alegre",
            peso_carga=500,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )

        # Criar atribuição
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido,
            motorista=motorista,
            veiculo=veiculo,
            status=StatusAtribuicao.EM_ANDAMENTO,
        )

        return {
            "atribuicao": atribuicao,
            "motorista": motorista,
            "pedido": pedido,
        }

    def test_criar_problema_sucesso(self, setup_problema):
        """Testa criação de problema com dados válidos."""
        data = setup_problema
        problema = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.VEICULO,
            descricao="Pneu furou durante o trajeto",
        )

        assert problema.id is not None
        assert problema.atribuicao == data["atribuicao"]
        assert problema.tipo == TipoProblema.VEICULO
        assert problema.descricao == "Pneu furou durante o trajeto"
        assert problema.status == StatusProblema.PENDENTE
        assert problema.resolucao is None
        assert problema.resolvido_em is None

    def test_problema_str(self, setup_problema):
        """Testa representação em string do problema."""
        data = setup_problema
        problema = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.ACIDENTE,
            descricao="Acidente leve no trajeto",
        )

        expected = f"Acidente - Pedido #{data['pedido'].id} - Pendente"
        assert str(problema) == expected

    def test_problema_status_default(self, setup_problema):
        """Testa que o status padrão é PENDENTE."""
        data = setup_problema
        problema = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.CARGA,
            descricao="Carga danificada",
        )

        assert problema.status == StatusProblema.PENDENTE

    def test_tipos_problema_validos(self):
        """Testa que todos os tipos de problema estão disponíveis."""
        tipos = [t.value for t in TipoProblema]
        assert "veiculo" in tipos
        assert "carga" in tipos
        assert "rota" in tipos
        assert "cliente" in tipos
        assert "acidente" in tipos
        assert "outro" in tipos

    def test_status_problema_validos(self):
        """Testa que todos os status de problema estão disponíveis."""
        status = [s.value for s in StatusProblema]
        assert "pendente" in status
        assert "em_analise" in status
        assert "resolvido" in status

    def test_problema_properties(self, setup_problema):
        """Testa as properties do problema."""
        data = setup_problema
        problema = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.ROTA,
            descricao="Estrada interditada",
        )

        assert problema.is_pendente is True
        assert problema.is_em_analise is False
        assert problema.is_resolvido is False

        problema.status = StatusProblema.EM_ANALISE
        problema.save()

        assert problema.is_pendente is False
        assert problema.is_em_analise is True
        assert problema.is_resolvido is False

        problema.status = StatusProblema.RESOLVIDO
        problema.resolvido_em = timezone.now()
        problema.save()

        assert problema.is_pendente is False
        assert problema.is_em_analise is False
        assert problema.is_resolvido is True

    def test_problema_motorista_property(self, setup_problema):
        """Testa atalho para acessar motorista."""
        data = setup_problema
        problema = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.OUTRO,
            descricao="Problema genérico",
        )

        assert problema.motorista == data["motorista"]

    def test_problema_pedido_property(self, setup_problema):
        """Testa atalho para acessar pedido."""
        data = setup_problema
        problema = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.CLIENTE,
            descricao="Cliente não estava no local",
        )

        assert problema.pedido == data["pedido"]

    def test_multiplos_problemas_mesma_atribuicao(self, setup_problema):
        """Testa que uma atribuição pode ter múltiplos problemas."""
        data = setup_problema

        problema1 = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.VEICULO,
            descricao="Primeiro problema",
        )

        problema2 = ProblemaEntrega.objects.create(
            atribuicao=data["atribuicao"],
            tipo=TipoProblema.ROTA,
            descricao="Segundo problema",
        )

        problemas = data["atribuicao"].problemas.all()
        assert problemas.count() == 2
        assert problema1 in problemas
        assert problema2 in problemas
