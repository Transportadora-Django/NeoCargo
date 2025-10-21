"""
Testes para a calculadora de custos de transporte.
"""

from django.test import TestCase
from decimal import Decimal
from apps.pedidos.calculadora import CalculadoraCustos
from apps.veiculos.models import Veiculo, EspecificacaoVeiculo, TipoVeiculo, TipoCombustivel
from apps.rotas.models import Cidade, Rota, Estado, ConfiguracaoPreco


class CalculadoraCustosTest(TestCase):
    """Testes para a CalculadoraCustos."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar configuração de preços
        self.config = ConfiguracaoPreco.objects.create(
            preco_alcool=Decimal("3.499"),
            preco_gasolina=Decimal("4.449"),
            preco_diesel=Decimal("3.869"),
            margem_lucro=Decimal("20.00"),
        )

        # Criar especificação de carreta
        self.espec_carreta = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRETA,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=8.0,
            carga_maxima=30000.0,
            velocidade_media=60,
            reducao_rendimento_principal=0.0002,
        )

        # Criar especificação de van
        self.espec_van = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.VAN,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=10.0,
            carga_maxima=3500.0,
            velocidade_media=80,
            reducao_rendimento_principal=0.001,
        )

        # Criar veículos
        self.veiculo_carreta = Veiculo.objects.create(
            especificacao=self.espec_carreta,
            marca="Scania",
            modelo="R450",
            placa="ABC1234",
            ano=2022,
            cor="Branco",
            ativo=True,
        )

        self.veiculo_van = Veiculo.objects.create(
            especificacao=self.espec_van,
            marca="Ford",
            modelo="Transit",
            placa="DEF5678",
            ano=2022,
            cor="Branco",
            ativo=True,
        )

        # Criar cidades
        self.cidade_sp = Cidade.objects.create(
            nome="São Paulo", estado=Estado.SP, latitude=Decimal("-23.5505199"), longitude=Decimal("-46.6333094")
        )

        self.cidade_rj = Cidade.objects.create(
            nome="Rio de Janeiro", estado=Estado.RJ, latitude=Decimal("-22.9068467"), longitude=Decimal("-43.1728965")
        )

        # Criar rota
        self.rota = Rota.objects.create(
            origem=self.cidade_sp,
            destino=self.cidade_rj,
            distancia_km=Decimal("430"),
            tempo_estimado_horas=Decimal("6.5"),
            pedagio_valor=Decimal("45.80"),
        )

        self.calculadora = CalculadoraCustos()

    def test_calcular_rendimento_final(self):
        """Testa cálculo de rendimento final com redução por peso."""
        # Carreta: 8 Km/L - (1000 kg * 0.0002) = 8 - 0.2 = 7.8 Km/L
        rendimento = self.calculadora.calcular_rendimento_final(
            rendimento_base=Decimal("8.0"), peso_carga_kg=Decimal("1000"), reducao_por_kg=Decimal("0.0002")
        )
        self.assertEqual(rendimento, Decimal("7.8"))

    def test_calcular_tempo_viagem(self):
        """Testa cálculo de tempo de viagem."""
        # 430 km / 60 km/h = 7.166... horas
        tempo = self.calculadora.calcular_tempo_viagem(distancia_km=Decimal("430"), velocidade_media=60)
        self.assertAlmostEqual(float(tempo), 7.1667, places=2)

    def test_calcular_custo_veiculo_carreta(self):
        """Testa cálculo de custo para carreta."""
        resultado = self.calculadora.calcular_custo_veiculo(
            veiculo=self.veiculo_carreta,
            peso_carga_kg=Decimal("10000"),  # 10 toneladas
            distancia_km=Decimal("430"),
            tempo_maximo_horas=Decimal("24"),
            pedagio_valor=Decimal("45.80"),
        )

        self.assertTrue(resultado.pode_transportar)
        self.assertEqual(resultado.veiculo, self.veiculo_carreta)
        self.assertEqual(resultado.combustivel_usado, TipoCombustivel.DIESEL)

        # Verificar cálculos
        # Rendimento: 8 - (10000 * 0.0002) = 8 - 2 = 6 Km/L
        self.assertEqual(resultado.rendimento_final, Decimal("6"))

        # Litros: 430 / 6 = 71.666... L
        self.assertAlmostEqual(float(resultado.litros_necessarios), 71.67, places=1)

        # Custo combustível: 71.67 * 3.869 = ~277.27
        self.assertGreater(resultado.custo_combustivel, Decimal("270"))
        self.assertLess(resultado.custo_combustivel, Decimal("280"))

    def test_calcular_custo_veiculo_excede_peso(self):
        """Testa que veículo não pode transportar carga acima do limite."""
        resultado = self.calculadora.calcular_custo_veiculo(
            veiculo=self.veiculo_van,
            peso_carga_kg=Decimal("5000"),  # Van suporta apenas 3500 kg
            distancia_km=Decimal("430"),
            tempo_maximo_horas=Decimal("24"),
            pedagio_valor=Decimal("45.80"),
        )

        self.assertFalse(resultado.pode_transportar)
        self.assertIn("excede limite", resultado.motivo_recusa)

    def test_calcular_custo_veiculo_excede_tempo(self):
        """Testa que veículo não pode atender prazo muito curto."""
        resultado = self.calculadora.calcular_custo_veiculo(
            veiculo=self.veiculo_carreta,
            peso_carga_kg=Decimal("1000"),
            distancia_km=Decimal("430"),
            tempo_maximo_horas=Decimal("2"),  # Impossível fazer em 2 horas
            pedagio_valor=Decimal("45.80"),
        )

        self.assertFalse(resultado.pode_transportar)
        self.assertIn("excede limite", resultado.motivo_recusa)

    def test_calcular_melhor_opcao(self):
        """Testa cálculo das 3 melhores opções."""
        resultados = self.calculadora.calcular_melhor_opcao(
            peso_carga_kg=Decimal("2000"),
            distancia_km=Decimal("430"),
            tempo_maximo_horas=Decimal("24"),
            pedagio_valor=Decimal("45.80"),
        )

        # Deve retornar as 3 opções
        self.assertIsNotNone(resultados["menor_custo"])
        self.assertIsNotNone(resultados["mais_rapido"])
        self.assertIsNotNone(resultados["melhor_custo_beneficio"])

        # Van deve ser mais rápida (80 km/h vs 60 km/h)
        self.assertEqual(resultados["mais_rapido"].veiculo.especificacao.tipo, TipoVeiculo.VAN)

        # Van deve ser mais econômica (10 km/L vs 8 km/L = menos litros)
        self.assertEqual(resultados["menor_custo"].veiculo.especificacao.tipo, TipoVeiculo.VAN)

        # Verificar que o mais rápido tem menor ou igual tempo
        self.assertLessEqual(
            resultados["mais_rapido"].tempo_viagem_horas,
            resultados["menor_custo"].tempo_viagem_horas,
        )

        # Verificar que o mais econômico tem menor ou igual consumo
        self.assertLessEqual(
            resultados["menor_custo"].litros_necessarios,
            resultados["mais_rapido"].litros_necessarios,
        )

        # Todos devem poder transportar
        self.assertTrue(resultados["menor_custo"].pode_transportar)
        self.assertTrue(resultados["mais_rapido"].pode_transportar)
        self.assertTrue(resultados["melhor_custo_beneficio"].pode_transportar)

    def test_calcular_melhor_opcao_sem_veiculos_disponiveis(self):
        """Testa quando nenhum veículo pode atender."""
        resultados = self.calculadora.calcular_melhor_opcao(
            peso_carga_kg=Decimal("50000"),  # Nenhum veículo suporta
            distancia_km=Decimal("430"),
            tempo_maximo_horas=Decimal("24"),
            pedagio_valor=Decimal("45.80"),
        )

        # Não deve retornar opções
        self.assertIsNone(resultados["menor_custo"])
        self.assertIsNone(resultados["mais_rapido"])
        self.assertIsNone(resultados["melhor_custo_beneficio"])

    def test_calcular_para_rota(self):
        """Testa cálculo usando uma rota específica."""
        resultados = self.calculadora.calcular_para_rota(
            rota=self.rota, peso_carga_kg=Decimal("2000"), tempo_maximo_horas=Decimal("24")
        )

        self.assertIsNotNone(resultados["menor_custo"])
        self.assertIsNotNone(resultados["mais_rapido"])
        self.assertIsNotNone(resultados["melhor_custo_beneficio"])

    def test_margem_lucro_aplicada(self):
        """Testa se a margem de lucro é aplicada corretamente."""
        resultado = self.calculadora.calcular_custo_veiculo(
            veiculo=self.veiculo_carreta,
            peso_carga_kg=Decimal("1000"),
            distancia_km=Decimal("100"),
            tempo_maximo_horas=None,
            pedagio_valor=Decimal("10"),
        )

        # Custo com margem deve ser 20% maior que custo total
        custo_esperado = resultado.custo_total * Decimal("1.20")
        self.assertAlmostEqual(float(resultado.custo_com_margem), float(custo_esperado), places=2)

    def test_veiculos_inativos_nao_sao_considerados(self):
        """Testa que veículos inativos não são considerados."""
        # Desativar todos os veículos
        Veiculo.objects.all().update(ativo=False)

        resultados = self.calculadora.calcular_melhor_opcao(
            peso_carga_kg=Decimal("1000"),
            distancia_km=Decimal("430"),
            tempo_maximo_horas=Decimal("24"),
            pedagio_valor=Decimal("45.80"),
        )

        # Não deve retornar opções
        self.assertIsNone(resultados["menor_custo"])
