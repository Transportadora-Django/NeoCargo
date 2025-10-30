"""Testes para os modelos do app motoristas."""

import pytest
from django.db.utils import IntegrityError

from apps.contas.models import Profile, Role
from apps.motoristas.models import (
    AtribuicaoPedido,
    CategoriaCNH,
    Motorista,
    StatusAtribuicao,
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
