from django.test import TestCase
from apps.veiculos.models import TipoVeiculo, TipoCombustivel, EspecificacaoVeiculo, Veiculo


class EspecificacaoVeiculoModelTest(TestCase):
    """Testes para o modelo EspecificacaoVeiculo"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.especificacao = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRETA,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=3.5,
            carga_maxima=30000,
            velocidade_media=80,
            reducao_rendimento_principal=0.001,
        )

    def test_criar_especificacao_veiculo(self):
        """Testa a criação de uma especificação de veículo"""
        self.assertEqual(self.especificacao.tipo, TipoVeiculo.CARRETA)
        self.assertEqual(self.especificacao.combustivel_principal, TipoCombustivel.DIESEL)
        self.assertEqual(self.especificacao.rendimento_principal, 3.5)
        self.assertEqual(self.especificacao.carga_maxima, 30000)
        self.assertEqual(self.especificacao.velocidade_media, 80)

    def test_str_especificacao_veiculo(self):
        """Testa a representação em string da especificação"""
        self.assertEqual(str(self.especificacao), "Carreta")

    def test_tipo_unico(self):
        """Testa que o tipo de veículo deve ser único"""
        with self.assertRaises(Exception):
            EspecificacaoVeiculo.objects.create(
                tipo=TipoVeiculo.CARRETA,  # Mesmo tipo
                combustivel_principal=TipoCombustivel.GASOLINA,
                rendimento_principal=5.0,
                carga_maxima=1000,
                velocidade_media=100,
                reducao_rendimento_principal=0.001,
            )

    def test_combustivel_alternativo_opcional(self):
        """Testa que combustível alternativo é opcional"""
        especificacao = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.VAN,
            combustivel_principal=TipoCombustivel.GASOLINA,
            combustivel_alternativo=TipoCombustivel.ALCOOL,
            rendimento_principal=10.0,
            rendimento_alternativo=7.0,
            carga_maxima=1500,
            velocidade_media=100,
            reducao_rendimento_principal=0.001,
            reducao_rendimento_alternativo=0.0015,
        )
        self.assertEqual(especificacao.combustivel_alternativo, TipoCombustivel.ALCOOL)
        self.assertEqual(especificacao.rendimento_alternativo, 7.0)


class VeiculoModelTest(TestCase):
    """Testes para o modelo Veiculo"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.especificacao = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRO,
            combustivel_principal=TipoCombustivel.GASOLINA,
            rendimento_principal=12.0,
            carga_maxima=500,
            velocidade_media=110,
            reducao_rendimento_principal=0.001,
        )

        self.veiculo = Veiculo.objects.create(
            especificacao=self.especificacao,
            marca="Ford",
            modelo="Fiesta",
            placa="ABC-1234",
            ano=2020,
            cor="Branco",
            ativo=True,
        )

    def test_criar_veiculo(self):
        """Testa a criação de um veículo"""
        self.assertEqual(self.veiculo.marca, "Ford")
        self.assertEqual(self.veiculo.modelo, "Fiesta")
        self.assertEqual(self.veiculo.placa, "ABC-1234")
        self.assertEqual(self.veiculo.ano, 2020)
        self.assertEqual(self.veiculo.cor, "Branco")
        self.assertTrue(self.veiculo.ativo)

    def test_str_veiculo(self):
        """Testa a representação em string do veículo"""
        self.assertEqual(str(self.veiculo), "Ford Fiesta - ABC-1234")

    def test_placa_unica(self):
        """Testa que a placa deve ser única"""
        with self.assertRaises(Exception):
            Veiculo.objects.create(
                especificacao=self.especificacao,
                marca="Chevrolet",
                modelo="Onix",
                placa="ABC-1234",  # Mesma placa
                ano=2021,
                cor="Preto",
                ativo=True,
            )

    def test_veiculo_inativo(self):
        """Testa criação de veículo inativo"""
        veiculo_inativo = Veiculo.objects.create(
            especificacao=self.especificacao,
            marca="Volkswagen",
            modelo="Gol",
            placa="XYZ-9876",
            ano=2015,
            cor="Prata",
            ativo=False,
        )
        self.assertFalse(veiculo_inativo.ativo)

    def test_relacionamento_especificacao(self):
        """Testa o relacionamento com especificação"""
        self.assertEqual(self.veiculo.especificacao, self.especificacao)
        self.assertEqual(self.veiculo.especificacao.tipo, TipoVeiculo.CARRO)

    def test_timestamps(self):
        """Testa que os timestamps são criados automaticamente"""
        self.assertIsNotNone(self.veiculo.created_at)
        self.assertIsNotNone(self.veiculo.updated_at)
