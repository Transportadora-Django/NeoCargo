from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from apps.pedidos.models import Pedido, StatusPedido
from apps.rotas.models import Cidade, Rota, Estado


class PedidoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

        # Criar cidades de teste
        self.sp = Cidade.objects.create(nome="São Paulo", estado=Estado.SP, ativa=True)
        self.rj = Cidade.objects.create(nome="Rio de Janeiro", estado=Estado.RJ, ativa=True)

        # Criar rota entre as cidades
        self.rota = Rota.objects.create(
            origem=self.sp, destino=self.rj, distancia_km=429.5, pedagio_valor=15.50, ativa=True
        )

    def test_criar_pedido_get(self):
        """Testa acesso à página de criar pedido"""
        response = self.client.get(reverse("pedidos:criar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Novo Pedido")
        self.assertContains(response, "form")

    def test_criar_pedido_post_valido(self):
        """Testa criação de pedido com dados válidos"""
        data = {
            "cidade_origem": "São Paulo - São Paulo",
            "cidade_destino": "Rio de Janeiro - Rio de Janeiro",
            "peso_carga": "100.50",
            "prazo_desejado": 7,
            "observacoes": "Carga frágil",
        }

        response = self.client.post(reverse("pedidos:criar"), data)

        # Deve redirecionar para cotação
        self.assertEqual(response.status_code, 302)
        pedido = Pedido.objects.first()

        # Verifica se pedido foi criado
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(pedido.cliente, self.user)
        self.assertEqual(pedido.cidade_origem, "São Paulo - São Paulo")
        self.assertEqual(pedido.status, StatusPedido.COTACAO)

        # Tenta acessar cotação (formato antigo redireciona para listar)
        response_cotacao = self.client.get(reverse("pedidos:gerar_cotacao", args=[pedido.id]))
        self.assertEqual(response_cotacao.status_code, 302)  # Redireciona pois não tem rota

    def test_criar_pedido_post_invalido(self):
        """Testa criação com dados inválidos"""
        data = {
            "cidade_origem": "",  # Campo obrigatório vazio
            "cidade_destino": "Rio de Janeiro",
            "peso_carga": "100.50",
            "prazo_desejado": 7,
        }

        response = self.client.post(reverse("pedidos:criar"), data)

        # Deve retornar o formulário com erro
        self.assertEqual(response.status_code, 200)
        # Verifica que o pedido não foi criado
        self.assertEqual(Pedido.objects.count(), 0)

    def test_listar_pedidos_vazio(self):
        """Testa listagem quando não há pedidos"""
        response = self.client.get(reverse("pedidos:listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "pedidos")

    def test_listar_pedidos_com_dados(self):
        """Testa listagem com pedidos"""
        # Criar alguns pedidos
        Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
        )

        response = self.client.get(reverse("pedidos:listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "São Paulo")
        self.assertContains(response, "Rio de Janeiro")

    def test_cancelar_pedido_pendente(self):
        """Testa cancelamento de pedido pendente"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
            status=StatusPedido.PENDENTE,
        )

        response = self.client.post(reverse("pedidos:cancelar", args=[pedido.id]))

        # Deve redirecionar
        self.assertEqual(response.status_code, 302)

        # Verifica se foi cancelado
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, StatusPedido.CANCELADO)

    def test_cancelar_pedido_aprovado(self):
        """Testa tentativa de cancelar pedido aprovado"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
            status=StatusPedido.APROVADO,
        )

        response = self.client.post(reverse("pedidos:cancelar", args=[pedido.id]))

        # Deve redirecionar
        self.assertEqual(response.status_code, 302)

        # Status não deve ter mudado
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, StatusPedido.APROVADO)

    def test_acesso_sem_login(self):
        """Testa acesso às views sem estar logado"""
        self.client.logout()

        urls = [
            reverse("pedidos:criar"),
            reverse("pedidos:listar"),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect para login
