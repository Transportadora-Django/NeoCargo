from django.test import TestCase
from apps.veiculos.models import TipoVeiculo, TipoCombustivel, EspecificacaoVeiculo
from apps.veiculos.forms import EspecificacaoVeiculoForm, VeiculoForm


class EspecificacaoVeiculoFormTest(TestCase):
    """Testes para o formulário de especificação de veículo"""

    def test_form_valido(self):
        """Testa formulário com dados válidos"""
        data = {
            "tipo": TipoVeiculo.CARRETA,
            "combustivel_principal": TipoCombustivel.DIESEL,
            "rendimento_principal": 3.5,
            "carga_maxima": 30000,
            "velocidade_media": 80,
            "reducao_rendimento_principal": 0.001,
        }
        form = EspecificacaoVeiculoForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_com_combustivel_alternativo(self):
        """Testa formulário com combustível alternativo"""
        data = {
            "tipo": TipoVeiculo.VAN,
            "combustivel_principal": TipoCombustivel.GASOLINA,
            "combustivel_alternativo": TipoCombustivel.ALCOOL,
            "rendimento_principal": 10.0,
            "rendimento_alternativo": 7.0,
            "carga_maxima": 1500,
            "velocidade_media": 100,
            "reducao_rendimento_principal": 0.001,
            "reducao_rendimento_alternativo": 0.0015,
        }
        form = EspecificacaoVeiculoForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_sem_tipo(self):
        """Testa formulário sem tipo (campo obrigatório)"""
        data = {
            "combustivel_principal": TipoCombustivel.DIESEL,
            "rendimento_principal": 3.5,
            "carga_maxima": 30000,
            "velocidade_media": 80,
            "reducao_rendimento_principal": 0.001,
        }
        form = EspecificacaoVeiculoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("tipo", form.errors)

    def test_form_sem_rendimento_principal(self):
        """Testa formulário sem rendimento principal (campo obrigatório)"""
        data = {
            "tipo": TipoVeiculo.CARRO,
            "combustivel_principal": TipoCombustivel.GASOLINA,
            "carga_maxima": 500,
            "velocidade_media": 110,
            "reducao_rendimento_principal": 0.001,
        }
        form = EspecificacaoVeiculoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("rendimento_principal", form.errors)


class VeiculoFormTest(TestCase):
    """Testes para o formulário de veículo"""

    def setUp(self):
        """Configuração inicial"""
        self.especificacao = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRO,
            combustivel_principal=TipoCombustivel.GASOLINA,
            rendimento_principal=12.0,
            carga_maxima=500,
            velocidade_media=110,
            reducao_rendimento_principal=0.001,
        )

    def test_form_valido(self):
        """Testa formulário com dados válidos"""
        data = {
            "especificacao": self.especificacao.id,
            "marca": "Ford",
            "modelo": "Fiesta",
            "placa": "ABC-1234",
            "ano": 2020,
            "cor": "Branco",
            "ativo": True,
        }
        form = VeiculoForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_sem_marca(self):
        """Testa formulário sem marca (campo obrigatório)"""
        data = {
            "especificacao": self.especificacao.id,
            "modelo": "Fiesta",
            "placa": "ABC-1234",
            "ano": 2020,
            "cor": "Branco",
            "ativo": True,
        }
        form = VeiculoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("marca", form.errors)

    def test_form_sem_placa(self):
        """Testa formulário sem placa (campo obrigatório)"""
        data = {
            "especificacao": self.especificacao.id,
            "marca": "Ford",
            "modelo": "Fiesta",
            "ano": 2020,
            "cor": "Branco",
            "ativo": True,
        }
        form = VeiculoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("placa", form.errors)

    def test_form_sem_especificacao(self):
        """Testa formulário sem especificação (campo obrigatório)"""
        data = {"marca": "Ford", "modelo": "Fiesta", "placa": "ABC-1234", "ano": 2020, "cor": "Branco", "ativo": True}
        form = VeiculoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("especificacao", form.errors)

    def test_form_veiculo_inativo(self):
        """Testa formulário com veículo inativo"""
        data = {
            "especificacao": self.especificacao.id,
            "marca": "Volkswagen",
            "modelo": "Gol",
            "placa": "XYZ-9876",
            "ano": 2015,
            "cor": "Prata",
            "ativo": False,
        }
        form = VeiculoForm(data=data)
        self.assertTrue(form.is_valid())
