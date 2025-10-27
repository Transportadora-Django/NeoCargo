"""
Testes para os models do app Rotas.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.rotas.models import Cidade, Rota, Estado, ConfiguracaoPreco


class CidadeModelTest(TestCase):
    """Testes para o model Cidade."""

    def test_criar_cidade(self):
        """Testa criação de cidade."""
        cidade = Cidade.objects.create(
            nome="São Paulo",
            estado=Estado.SP,
            latitude=Decimal("-23.5505199"),
            longitude=Decimal("-46.6333094"),
            ativa=True,
        )

        self.assertEqual(cidade.nome, "São Paulo")
        self.assertEqual(cidade.estado, Estado.SP)
        self.assertTrue(cidade.ativa)

    def test_nome_completo(self):
        """Testa propriedade nome_completo."""
        cidade = Cidade.objects.create(nome="São Paulo", estado=Estado.SP)
        self.assertEqual(cidade.nome_completo, "São Paulo/SP")

    def test_str_representation(self):
        """Testa representação em string."""
        cidade = Cidade.objects.create(nome="Rio de Janeiro", estado=Estado.RJ)
        self.assertEqual(str(cidade), "Rio de Janeiro - RJ")

    def test_unique_together_cidade_estado(self):
        """Testa que não pode ter cidade duplicada no mesmo estado."""
        Cidade.objects.create(nome="São Paulo", estado=Estado.SP)

        with self.assertRaises(Exception):
            Cidade.objects.create(nome="São Paulo", estado=Estado.SP)

    def test_cidade_pode_ser_desativada(self):
        """Testa que cidade pode ser desativada."""
        cidade = Cidade.objects.create(nome="São Paulo", estado=Estado.SP, ativa=True)
        cidade.ativa = False
        cidade.save()

        self.assertFalse(cidade.ativa)


class RotaModelTest(TestCase):
    """Testes para o model Rota."""

    def setUp(self):
        """Configuração inicial."""
        self.cidade_sp = Cidade.objects.create(nome="São Paulo", estado=Estado.SP)
        self.cidade_rj = Cidade.objects.create(nome="Rio de Janeiro", estado=Estado.RJ)

    def test_criar_rota(self):
        """Testa criação de rota."""
        rota = Rota.objects.create(
            origem=self.cidade_sp,
            destino=self.cidade_rj,
            distancia_km=Decimal("430"),
            tempo_estimado_horas=Decimal("6.5"),
            pedagio_valor=Decimal("45.80"),
        )

        self.assertEqual(rota.origem, self.cidade_sp)
        self.assertEqual(rota.destino, self.cidade_rj)
        self.assertEqual(rota.distancia_km, Decimal("430"))

    def test_str_representation(self):
        """Testa representação em string."""
        rota = Rota.objects.create(origem=self.cidade_sp, destino=self.cidade_rj, distancia_km=Decimal("430"))

        expected = "São Paulo/SP → Rio de Janeiro/RJ (430 km)"
        self.assertEqual(str(rota), expected)

    def test_origem_nao_pode_ser_igual_destino(self):
        """Testa validação de origem diferente de destino."""
        rota = Rota(
            origem=self.cidade_sp,
            destino=self.cidade_sp,  # Mesma cidade
            distancia_km=Decimal("100"),
        )

        with self.assertRaises(ValidationError):
            rota.save()

    def test_custo_estimado_combustivel(self):
        """Testa cálculo de custo estimado de combustível."""
        rota = Rota.objects.create(origem=self.cidade_sp, destino=self.cidade_rj, distancia_km=Decimal("430"))

        # 430 km * R$ 0.80/km = R$ 344.00
        self.assertEqual(rota.custo_estimado_combustivel, Decimal("344.00"))

    def test_custo_total_estimado(self):
        """Testa cálculo de custo total estimado."""
        rota = Rota.objects.create(
            origem=self.cidade_sp,
            destino=self.cidade_rj,
            distancia_km=Decimal("430"),
            pedagio_valor=Decimal("45.80"),
        )

        # Combustível (344.00) + Pedágio (45.80) = 389.80
        self.assertEqual(rota.custo_total_estimado, Decimal("389.80"))

    def test_rota_pode_ser_desativada(self):
        """Testa que rota pode ser desativada."""
        rota = Rota.objects.create(
            origem=self.cidade_sp, destino=self.cidade_rj, distancia_km=Decimal("430"), ativa=True
        )

        rota.ativa = False
        rota.save()

        self.assertFalse(rota.ativa)

    def test_unique_together_origem_destino(self):
        """Testa que não pode ter rota duplicada."""
        Rota.objects.create(origem=self.cidade_sp, destino=self.cidade_rj, distancia_km=Decimal("430"))

        with self.assertRaises(Exception):
            Rota.objects.create(origem=self.cidade_sp, destino=self.cidade_rj, distancia_km=Decimal("500"))


class ConfiguracaoPrecoModelTest(TestCase):
    """Testes para o model ConfiguracaoPreco."""

    def test_criar_configuracao(self):
        """Testa criação de configuração."""
        config = ConfiguracaoPreco.objects.create(
            preco_alcool=Decimal("3.499"),
            preco_gasolina=Decimal("4.449"),
            preco_diesel=Decimal("3.869"),
            margem_lucro=Decimal("20.00"),
        )

        self.assertEqual(config.preco_alcool, Decimal("3.499"))
        self.assertEqual(config.preco_gasolina, Decimal("4.449"))
        self.assertEqual(config.preco_diesel, Decimal("3.869"))
        self.assertEqual(config.margem_lucro, Decimal("20.00"))

    def test_get_atual_cria_se_nao_existe(self):
        """Testa que get_atual cria configuração se não existir."""
        # Garantir que não existe
        ConfiguracaoPreco.objects.all().delete()

        config = ConfiguracaoPreco.get_atual()

        self.assertIsNotNone(config)
        self.assertEqual(config.preco_alcool, Decimal("3.499"))
        self.assertEqual(config.preco_gasolina, Decimal("4.449"))
        self.assertEqual(config.preco_diesel, Decimal("3.869"))
        self.assertEqual(config.margem_lucro, Decimal("20.00"))

    def test_get_atual_retorna_mais_recente(self):
        """Testa que get_atual retorna a configuração mais recente."""
        # Criar duas configurações
        ConfiguracaoPreco.objects.create(preco_alcool=Decimal("3.00"))
        config2 = ConfiguracaoPreco.objects.create(preco_alcool=Decimal("4.00"))

        config_atual = ConfiguracaoPreco.get_atual()

        # Deve retornar a mais recente (config2)
        self.assertEqual(config_atual.id, config2.id)
        self.assertEqual(config_atual.preco_alcool, Decimal("4.00"))

    def test_str_representation(self):
        """Testa representação em string."""
        config = ConfiguracaoPreco.objects.create()
        str_repr = str(config)

        self.assertIn("Configuração de Preços", str_repr)
