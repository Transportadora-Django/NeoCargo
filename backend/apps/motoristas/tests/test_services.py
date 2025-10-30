"""Testes para o serviço de atribuição automática de motoristas."""

import pytest
from django.core.exceptions import ValidationError

from apps.contas.models import Profile, Role
from apps.motoristas.models import (
    AtribuicaoPedido,
    CategoriaCNH,
    Motorista,
    StatusAtribuicao,
)
from apps.motoristas.services import AtribuicaoService
from apps.pedidos.models import Pedido, StatusPedido
from apps.rotas.models import Cidade
from apps.veiculos.models import EspecificacaoVeiculo, TipoCombustivel, TipoVeiculo, Veiculo


@pytest.mark.django_db
class TestAtribuicaoServiceCNH:
    """Testes para validação de CNH."""

    def test_pode_dirigir_mesma_categoria(self):
        """Testa que motorista pode dirigir veículo da mesma categoria."""
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.C, CategoriaCNH.C)

    def test_cnh_d_pode_dirigir_b_c_d(self):
        """Testa que CNH D pode dirigir veículos B, C e D."""
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.D, CategoriaCNH.B)
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.D, CategoriaCNH.C)
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.D, CategoriaCNH.D)

    def test_cnh_d_nao_pode_dirigir_e(self):
        """Testa que CNH D não pode dirigir veículos categoria E."""
        assert not AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.D, CategoriaCNH.E)

    def test_cnh_c_pode_dirigir_b_c(self):
        """Testa que CNH C pode dirigir veículos B e C."""
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.C, CategoriaCNH.B)
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.C, CategoriaCNH.C)

    def test_cnh_c_nao_pode_dirigir_d_e(self):
        """Testa que CNH C não pode dirigir veículos D ou E."""
        assert not AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.C, CategoriaCNH.D)
        assert not AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.C, CategoriaCNH.E)

    def test_cnh_b_so_pode_dirigir_b(self):
        """Testa que CNH B só pode dirigir veículos categoria B."""
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.B, CategoriaCNH.B)
        assert not AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.B, CategoriaCNH.C)
        assert not AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.B, CategoriaCNH.D)
        assert not AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.B, CategoriaCNH.E)

    def test_cnh_e_pode_dirigir_todas(self):
        """Testa que CNH E pode dirigir veículos de todas as categorias."""
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.E, CategoriaCNH.B)
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.E, CategoriaCNH.C)
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.E, CategoriaCNH.D)
        assert AtribuicaoService.pode_dirigir_veiculo(CategoriaCNH.E, CategoriaCNH.E)


@pytest.mark.django_db
class TestAtribuicaoServiceBusca:
    """Testes para busca de motoristas e veículos."""

    @pytest.fixture
    def cidades(self):
        """Cria cidades de teste."""
        sp = Cidade.objects.create(nome="São Paulo", estado="SP", latitude=-23.5505, longitude=-46.6333)
        rj = Cidade.objects.create(nome="Rio de Janeiro", estado="RJ", latitude=-22.9068, longitude=-43.1729)
        return {"sp": sp, "rj": rj}

    @pytest.fixture
    def motoristas(self, django_user_model, cidades):
        """Cria motoristas de teste."""
        motoristas_list = []
        for i in range(3):
            user = django_user_model.objects.create_user(
                username=f"motorista_{i}",
                email=f"motorista{i}@test.com",
                password="senha123",
            )
            profile = Profile.objects.get(user=user)
            profile.role = Role.MOTORISTA
            profile.save()
            motorista = Motorista.objects.create(
                profile=profile,
                sede_atual=cidades["sp"],
                cnh_categoria=CategoriaCNH.D,
                disponivel=True,
                entregas_concluidas=i,  # Diferentes quantidades de entregas
            )
            motoristas_list.append(motorista)
        return motoristas_list

    @pytest.fixture
    def veiculos(self, cidades):
        """Cria veículos de teste."""
        espec = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRETA,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=3.5,
            carga_maxima=25000,
            velocidade_media=80,
            reducao_rendimento_principal=0.0001,
        )
        veiculos_list = []
        for i in range(2):
            veiculo = Veiculo.objects.create(
                especificacao=espec,
                marca="Scania",
                modelo=f"R450 {i}",
                placa=f"ABC{i}234",
                ano=2020,
                cor="Branco",
                sede_atual=cidades["sp"],
                categoria_minima_cnh=CategoriaCNH.C,
            )
            veiculos_list.append(veiculo)
        return veiculos_list

    def test_buscar_motorista_disponivel_na_cidade(self, cidades, motoristas):
        """Testa busca de motorista disponível na cidade correta."""
        motorista = AtribuicaoService.buscar_motorista_disponivel(cidades["sp"])
        assert motorista is not None
        assert motorista.sede_atual == cidades["sp"]
        assert motorista.disponivel is True

    def test_buscar_motorista_prioriza_menos_entregas(self, cidades, motoristas):
        """Testa que busca prioriza motoristas com menos entregas."""
        motorista = AtribuicaoService.buscar_motorista_disponivel(cidades["sp"])
        assert motorista.entregas_concluidas == 0

    def test_buscar_motorista_com_cnh_especifica(self, cidades, motoristas):
        """Testa busca de motorista com CNH específica."""
        motorista = AtribuicaoService.buscar_motorista_disponivel(cidades["sp"], cnh_minima=CategoriaCNH.D)
        assert motorista is not None
        assert AtribuicaoService.pode_dirigir_veiculo(motorista.cnh_categoria, CategoriaCNH.D)

    def test_buscar_motorista_nao_encontra_cidade_errada(self, cidades, motoristas):
        """Testa que não encontra motorista em cidade diferente."""
        motorista = AtribuicaoService.buscar_motorista_disponivel(cidades["rj"])
        assert motorista is None

    def test_buscar_motorista_nao_encontra_indisponiveis(self, cidades, motoristas, django_user_model):
        """Testa que não retorna motoristas indisponíveis."""
        # Marcar todos como indisponíveis
        for m in motoristas:
            m.disponivel = False
            m.save()

        motorista = AtribuicaoService.buscar_motorista_disponivel(cidades["sp"])
        assert motorista is None

    def test_buscar_veiculo_disponivel_na_cidade(self, cidades, veiculos):
        """Testa busca de veículo disponível na cidade correta."""
        veiculo = AtribuicaoService.buscar_veiculo_disponivel(cidades["sp"])
        assert veiculo is not None
        assert veiculo.sede_atual == cidades["sp"]

    def test_buscar_veiculo_compativel_com_motorista(self, cidades, veiculos, motoristas):
        """Testa busca de veículo compatível com CNH do motorista."""
        motorista = motoristas[0]
        veiculo = AtribuicaoService.buscar_veiculo_disponivel(cidades["sp"], motorista=motorista)
        assert veiculo is not None
        assert AtribuicaoService.pode_dirigir_veiculo(motorista.cnh_categoria, veiculo.categoria_minima_cnh)

    def test_buscar_veiculo_nao_encontra_ja_atribuido(self, cidades, veiculos, motoristas, django_user_model):
        """Testa que não retorna veículos já atribuídos."""
        # Criar um pedido e atribuir um veículo
        user_cliente = django_user_model.objects.create_user(
            username="cliente", email="cliente@test.com", password="senha123"
        )
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="São Paulo",
            cidade_destino="São Paulo",
            peso_carga=1000,
            prazo_desejado=3,
            status=StatusPedido.PENDENTE,
        )
        AtribuicaoPedido.objects.create(
            pedido=pedido,
            motorista=motoristas[0],
            veiculo=veiculos[0],
            status=StatusAtribuicao.EM_ANDAMENTO,
        )

        # Deve retornar o segundo veículo
        veiculo = AtribuicaoService.buscar_veiculo_disponivel(cidades["sp"])
        assert veiculo == veiculos[1]


@pytest.mark.django_db
class TestAtribuicaoServiceAtribuir:
    """Testes para atribuição automática de pedidos."""

    @pytest.fixture
    def setup_completo(self, django_user_model):
        """Configura um cenário completo para testes de atribuição."""
        # Criar cidade
        cidade = Cidade.objects.create(nome="Curitiba", estado="PR", latitude=-25.4284, longitude=-49.2733)

        # Criar motorista
        user_motorista = django_user_model.objects.create_user(
            username="motorista", email="motorista@test.com", password="senha123"
        )
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.D,
            disponivel=True,
            entregas_concluidas=0,
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
            marca="Volvo",
            modelo="FH",
            placa="XYZ9876",
            ano=2021,
            cor="Branco",
            sede_atual=cidade,
            categoria_minima_cnh=CategoriaCNH.C,
        )

        # Criar cliente e pedido
        user_cliente = django_user_model.objects.create_user(
            username="cliente", email="cliente@test.com", password="senha123"
        )
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Curitiba",
            cidade_destino="Curitiba",
            peso_carga=2000,
            prazo_desejado=3,
            status=StatusPedido.APROVADO,
        )

        return {
            "cidade": cidade,
            "motorista": motorista,
            "veiculo": veiculo,
            "pedido": pedido,
        }

    def test_atribuir_pedido_sucesso(self, setup_completo):
        """Testa atribuição bem-sucedida de pedido."""
        data = setup_completo
        atribuicao = AtribuicaoService.atribuir_pedido(data["pedido"])

        assert atribuicao is not None
        assert atribuicao.pedido == data["pedido"]
        assert atribuicao.motorista == data["motorista"]
        assert atribuicao.veiculo == data["veiculo"]
        assert atribuicao.status == StatusAtribuicao.PENDENTE

        # Verificar que motorista foi marcado como indisponível
        data["motorista"].refresh_from_db()
        assert data["motorista"].disponivel is False

        # Verificar que status do pedido foi atualizado
        data["pedido"].refresh_from_db()
        assert data["pedido"].status == StatusPedido.EM_TRANSPORTE

    def test_atribuir_pedido_sem_motorista_disponivel(self, setup_completo):
        """Testa erro quando não há motorista disponível."""
        data = setup_completo
        data["motorista"].disponivel = False
        data["motorista"].save()

        with pytest.raises(ValidationError, match="Não há motoristas disponíveis"):
            AtribuicaoService.atribuir_pedido(data["pedido"])

    def test_atribuir_pedido_sem_veiculo_disponivel(self, setup_completo, django_user_model):
        """Testa erro quando não há veículo disponível."""
        data = setup_completo

        # Criar outro pedido e atribuir o único veículo
        user_outro = django_user_model.objects.create_user(
            username="outro_cliente", email="outro@test.com", password="senha123"
        )
        profile_outro = Profile.objects.get(user=user_outro)
        profile_outro.role = Role.CLIENTE
        profile_outro.save()
        pedido_outro = Pedido.objects.create(
            cliente=user_outro,
            cidade_origem="Curitiba",
            cidade_destino="Curitiba",
            peso_carga=1000,
            prazo_desejado=3,
            status=StatusPedido.APROVADO,
        )
        AtribuicaoPedido.objects.create(
            pedido=pedido_outro,
            motorista=data["motorista"],
            veiculo=data["veiculo"],
            status=StatusAtribuicao.EM_ANDAMENTO,
        )

        # Criar segundo motorista para não falhar na busca de motorista
        # Mas com CNH B (não pode dirigir veículo categoria C)
        user_motorista2 = django_user_model.objects.create_user(
            username="motorista2", email="motorista2@test.com", password="senha123"
        )
        profile_motorista2 = Profile.objects.get(user=user_motorista2)
        profile_motorista2.role = Role.MOTORISTA
        profile_motorista2.save()
        Motorista.objects.create(
            profile=profile_motorista2,
            sede_atual=data["cidade"],
            cnh_categoria=CategoriaCNH.B,  # CNH B não pode dirigir veículo categoria C
            disponivel=True,
            entregas_concluidas=0,
        )

        with pytest.raises(ValidationError, match="Não há veículos disponíveis na cidade"):
            AtribuicaoService.atribuir_pedido(data["pedido"])


@pytest.mark.django_db
class TestAtribuicaoServiceConcluir:
    """Testes para conclusão de entregas."""

    @pytest.fixture
    def setup_entrega(self, django_user_model):
        """Configura uma entrega em andamento."""
        # Criar cidades
        origem = Cidade.objects.create(nome="Origem", estado="SP", latitude=-23.5, longitude=-46.6)
        destino = Cidade.objects.create(nome="Destino", estado="RJ", latitude=-22.9, longitude=-43.2)

        # Criar motorista
        user_motorista = django_user_model.objects.create_user(
            username="motorista", email="motorista@test.com", password="senha123"
        )
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
            modelo="Atego 1719",
            placa="DEF4567",
            ano=2019,
            cor="Branco",
            sede_atual=origem,
            categoria_minima_cnh=CategoriaCNH.C,
        )

        # Criar pedido e atribuição
        user_cliente = django_user_model.objects.create_user(
            username="cliente", email="cliente@test.com", password="senha123"
        )
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Origem",
            cidade_destino="Destino",
            peso_carga=1500,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido,
            motorista=motorista,
            veiculo=veiculo,
            status=StatusAtribuicao.EM_ANDAMENTO,
        )

        return {
            "origem": origem,
            "destino": destino,
            "motorista": motorista,
            "veiculo": veiculo,
            "pedido": pedido,
            "atribuicao": atribuicao,
        }

    def test_concluir_entrega_sucesso(self, setup_entrega):
        """Testa conclusão bem-sucedida de entrega."""
        data = setup_entrega
        AtribuicaoService.concluir_entrega(data["atribuicao"])

        # Verificar status da atribuição
        data["atribuicao"].refresh_from_db()
        assert data["atribuicao"].status == StatusAtribuicao.CONCLUIDO

        # Verificar que motorista foi atualizado
        data["motorista"].refresh_from_db()
        assert data["motorista"].sede_atual == data["destino"]
        assert data["motorista"].disponivel is True
        assert data["motorista"].entregas_concluidas == 6

        # Verificar que veículo foi atualizado
        data["veiculo"].refresh_from_db()
        assert data["veiculo"].sede_atual == data["destino"]

        # Verificar status do pedido
        data["pedido"].refresh_from_db()
        assert data["pedido"].status == StatusPedido.CONCLUIDO


@pytest.mark.django_db
class TestAtribuicaoServiceCancelar:
    """Testes para cancelamento de atribuições."""

    @pytest.fixture
    def setup_cancelamento(self, django_user_model):
        """Configura uma atribuição para cancelamento."""
        # Criar cidade
        cidade = Cidade.objects.create(nome="Cidade", estado="SP", latitude=-23.5, longitude=-46.6)

        # Criar motorista
        user_motorista = django_user_model.objects.create_user(
            username="motorista", email="motorista@test.com", password="senha123"
        )
        profile_motorista = Profile.objects.get(user=user_motorista)
        profile_motorista.role = Role.MOTORISTA
        profile_motorista.save()
        motorista = Motorista.objects.create(
            profile=profile_motorista,
            sede_atual=cidade,
            cnh_categoria=CategoriaCNH.B,
            disponivel=False,
            entregas_concluidas=3,
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
            placa="GHI7890",
            ano=2018,
            cor="Branco",
            sede_atual=cidade,
            categoria_minima_cnh=CategoriaCNH.B,
        )

        # Criar pedido e atribuição
        user_cliente = django_user_model.objects.create_user(
            username="cliente", email="cliente@test.com", password="senha123"
        )
        profile_cliente = Profile.objects.get(user=user_cliente)
        profile_cliente.role = Role.CLIENTE
        profile_cliente.save()
        pedido = Pedido.objects.create(
            cliente=user_cliente,
            cidade_origem="Cidade",
            cidade_destino="Cidade",
            peso_carga=500,
            prazo_desejado=3,
            status=StatusPedido.EM_TRANSPORTE,
        )
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido,
            motorista=motorista,
            veiculo=veiculo,
            status=StatusAtribuicao.PENDENTE,
        )

        return {
            "motorista": motorista,
            "veiculo": veiculo,
            "pedido": pedido,
            "atribuicao": atribuicao,
        }

    def test_cancelar_atribuicao_sucesso(self, setup_cancelamento):
        """Testa cancelamento bem-sucedido de atribuição."""
        data = setup_cancelamento
        motivo = "Cliente cancelou o pedido"
        AtribuicaoService.cancelar_atribuicao(data["atribuicao"], motivo=motivo)

        # Verificar status da atribuição
        data["atribuicao"].refresh_from_db()
        assert data["atribuicao"].status == StatusAtribuicao.CANCELADO

        # Verificar que motorista ficou disponível novamente
        data["motorista"].refresh_from_db()
        assert data["motorista"].disponivel is True

        # Verificar status do pedido (volta para APROVADO para permitir nova atribuição)
        data["pedido"].refresh_from_db()
        assert data["pedido"].status == StatusPedido.APROVADO
