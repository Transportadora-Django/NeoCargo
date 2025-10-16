from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.contas.models import Profile, Role
from apps.veiculos.models import TipoVeiculo, TipoCombustivel, EspecificacaoVeiculo, Veiculo


class VeiculosViewsTest(TestCase):
    """Testes para as views do app veiculos"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = Client()

        # Criar usuário owner
        self.owner_user = User.objects.create_user(
            username="owner_test", password="testpass123", email="owner@test.com"
        )
        self.owner_profile = Profile.objects.get(user=self.owner_user)
        self.owner_profile.role = Role.OWNER
        self.owner_profile.save()

        # Criar usuário cliente (sem permissão)
        self.client_user = User.objects.create_user(
            username="client_test", password="testpass123", email="client@test.com"
        )
        self.client_profile = Profile.objects.get(user=self.client_user)
        self.client_profile.role = Role.CLIENTE
        self.client_profile.save()

        # Criar especificação
        self.especificacao = EspecificacaoVeiculo.objects.create(
            tipo=TipoVeiculo.CARRETA,
            combustivel_principal=TipoCombustivel.DIESEL,
            rendimento_principal=3.5,
            carga_maxima=30000,
            velocidade_media=80,
            reducao_rendimento_principal=0.001,
        )

        # Criar veículo
        self.veiculo = Veiculo.objects.create(
            especificacao=self.especificacao,
            marca="Scania",
            modelo="R450",
            placa="ABC-1234",
            ano=2020,
            cor="Branco",
            ativo=True,
        )

    def test_listar_veiculos_sem_autenticacao(self):
        """Testa que usuário não autenticado é redirecionado"""
        response = self.client.get(reverse("veiculos:listar_veiculos"))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_listar_veiculos_sem_permissao(self):
        """Testa que usuário sem permissão não acessa"""
        self.client.login(username="client_test", password="testpass123")
        response = self.client.get(reverse("veiculos:listar_veiculos"))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_listar_veiculos_com_permissao(self):
        """Testa listagem de veículos com permissão"""
        self.client.login(username="owner_test", password="testpass123")
        response = self.client.get(reverse("veiculos:listar_veiculos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scania")
        self.assertContains(response, "ABC-1234")

    def test_listar_especificacoes_com_permissao(self):
        """Testa listagem de especificações com permissão"""
        self.client.login(username="owner_test", password="testpass123")
        response = self.client.get(reverse("veiculos:listar_especificacoes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carreta")

    def test_adicionar_veiculo_get(self):
        """Testa acesso ao formulário de adicionar veículo"""
        self.client.login(username="owner_test", password="testpass123")
        response = self.client.get(reverse("veiculos:adicionar_veiculo"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar")

    def test_adicionar_veiculo_post(self):
        """Testa criação de veículo via POST"""
        self.client.login(username="owner_test", password="testpass123")
        data = {
            "especificacao": self.especificacao.id,
            "marca": "Volvo",
            "modelo": "FH16",
            "placa": "XYZ-9876",
            "ano": 2021,
            "cor": "Azul",
            "ativo": True,
        }
        response = self.client.post(reverse("veiculos:adicionar_veiculo"), data)
        self.assertEqual(response.status_code, 302)  # Redirect após sucesso
        self.assertTrue(Veiculo.objects.filter(placa="XYZ-9876").exists())

    def test_editar_veiculo_get(self):
        """Testa acesso ao formulário de editar veículo"""
        self.client.login(username="owner_test", password="testpass123")
        response = self.client.get(reverse("veiculos:editar_veiculo", args=[self.veiculo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scania")

    def test_editar_veiculo_post(self):
        """Testa edição de veículo via POST"""
        self.client.login(username="owner_test", password="testpass123")
        data = {
            "especificacao": self.especificacao.id,
            "marca": "Scania",
            "modelo": "R500",  # Mudando modelo
            "placa": "ABC-1234",
            "ano": 2020,
            "cor": "Preto",  # Mudando cor
            "ativo": True,
        }
        response = self.client.post(reverse("veiculos:editar_veiculo", args=[self.veiculo.id]), data)
        self.assertEqual(response.status_code, 302)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.modelo, "R500")
        self.assertEqual(self.veiculo.cor, "Preto")

    def test_remover_veiculo_get(self):
        """Testa acesso à página de confirmação de remoção"""
        self.client.login(username="owner_test", password="testpass123")
        response = self.client.get(reverse("veiculos:remover_veiculo", args=[self.veiculo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmar")

    def test_remover_veiculo_post(self):
        """Testa remoção de veículo via POST"""
        self.client.login(username="owner_test", password="testpass123")
        veiculo_id = self.veiculo.id
        response = self.client.post(reverse("veiculos:remover_veiculo", args=[veiculo_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Veiculo.objects.filter(id=veiculo_id).exists())

    def test_adicionar_especificacao_post(self):
        """Testa criação de especificação via POST"""
        self.client.login(username="owner_test", password="testpass123")
        data = {
            "tipo": TipoVeiculo.VAN,
            "combustivel_principal": TipoCombustivel.GASOLINA,
            "rendimento_principal": 10.0,
            "carga_maxima": 1500,
            "velocidade_media": 100,
            "reducao_rendimento_principal": 0.001,
        }
        response = self.client.post(reverse("veiculos:adicionar_especificacao"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EspecificacaoVeiculo.objects.filter(tipo=TipoVeiculo.VAN).exists())
