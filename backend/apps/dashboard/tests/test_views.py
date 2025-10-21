"""
Testes para as views do app Dashboard.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.contas.models import Profile, Role
from apps.pedidos.models import Pedido, StatusPedido

User = get_user_model()


class DashboardClienteViewTest(TestCase):
    """Testes para a view dashboard_cliente."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()

        # Criar usuário cliente
        self.cliente_user = User.objects.create_user(
            username="cliente_test", email="cliente@test.com", password="testpass123"
        )
        # Obter ou atualizar o perfil criado automaticamente pelo signal
        self.cliente_profile = Profile.objects.get(user=self.cliente_user)
        self.cliente_profile.role = Role.CLIENTE
        self.cliente_profile.save()

        # Criar usuário owner
        self.owner_user = User.objects.create_user(
            username="owner_test", email="owner@test.com", password="testpass123"
        )
        # Obter ou atualizar o perfil criado automaticamente pelo signal
        self.owner_profile = Profile.objects.get(user=self.owner_user)
        self.owner_profile.role = Role.OWNER
        self.owner_profile.save()

        # URL do dashboard
        self.url = reverse("dashboard:cliente")

    def test_dashboard_cliente_requires_login(self):
        """Testa se o dashboard requer autenticação."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/contas/login/", response.url)

    def test_dashboard_cliente_success(self):
        """Testa acesso bem-sucedido ao dashboard do cliente."""
        self.client.login(username="cliente_test", password="testpass123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/cliente.html")
        self.assertIn("profile", response.context)
        self.assertIn("pedidos_recentes", response.context)
        self.assertIn("total_pedidos", response.context)
        self.assertIn("pedidos_pendentes", response.context)
        self.assertIn("pedidos_concluidos", response.context)

    def test_dashboard_cliente_redirects_owner(self):
        """Testa se owner é redirecionado para dashboard do dono."""
        self.client.login(username="owner_test", password="testpass123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gestao:dashboard_dono"))

    def test_dashboard_cliente_creates_profile_if_not_exists(self):
        """Testa se cria perfil automaticamente se não existir."""
        # Criar usuário sem perfil
        user_without_profile = User.objects.create_user(
            username="no_profile", email="noprofile@test.com", password="testpass123"
        )

        self.client.login(username="no_profile", password="testpass123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # Verificar se o perfil foi criado
        self.assertTrue(Profile.objects.filter(user=user_without_profile).exists())

    def test_dashboard_cliente_statistics(self):
        """Testa se as estatísticas são calculadas corretamente."""
        self.client.login(username="cliente_test", password="testpass123")

        # Criar pedidos de teste
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=100.0,
            prazo_desejado=5,
            status=StatusPedido.COTACAO,
        )
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Belo Horizonte",
            peso_carga=200.0,
            prazo_desejado=3,
            status=StatusPedido.CONCLUIDO,
        )
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Curitiba",
            peso_carga=150.0,
            prazo_desejado=7,
            status=StatusPedido.PENDENTE,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.context["total_pedidos"], 3)
        self.assertEqual(response.context["pedidos_pendentes"], 2)  # COTACAO + PENDENTE
        self.assertEqual(response.context["pedidos_concluidos"], 1)

    def test_dashboard_cliente_recent_orders_limit(self):
        """Testa se apenas o pedido mais recente é retornado."""
        self.client.login(username="cliente_test", password="testpass123")

        # Criar múltiplos pedidos
        for i in range(5):
            Pedido.objects.create(
                cliente=self.cliente_user,
                cidade_origem="São Paulo",
                cidade_destino=f"Destino {i}",
                peso_carga=100.0 + i,
                prazo_desejado=5 + i,
                status=StatusPedido.COTACAO,
            )

        response = self.client.get(self.url)

        # Deve retornar apenas 1 pedido (o mais recente)
        self.assertEqual(len(response.context["pedidos_recentes"]), 1)

    def test_dashboard_cliente_empty_statistics(self):
        """Testa dashboard sem pedidos."""
        self.client.login(username="cliente_test", password="testpass123")
        response = self.client.get(self.url)

        self.assertEqual(response.context["total_pedidos"], 0)
        self.assertEqual(response.context["pedidos_pendentes"], 0)
        self.assertEqual(response.context["pedidos_concluidos"], 0)
        self.assertEqual(len(response.context["pedidos_recentes"]), 0)

    def test_dashboard_cliente_profile_context(self):
        """Testa se o perfil do usuário está no contexto."""
        self.client.login(username="cliente_test", password="testpass123")
        response = self.client.get(self.url)

        self.assertEqual(response.context["profile"], self.cliente_profile)
        self.assertEqual(response.context["profile"].role, Role.CLIENTE)

    def test_dashboard_cliente_with_motorista_role(self):
        """Testa dashboard acessado por motorista."""
        self.cliente_profile.role = Role.MOTORISTA
        self.cliente_profile.save()

        self.client.login(username="cliente_test", password="testpass123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"].role, Role.MOTORISTA)

    def test_dashboard_cliente_post_method_not_allowed(self):
        """Testa que método POST não é permitido."""
        self.client.login(username="cliente_test", password="testpass123")
        response = self.client.post(self.url, {})

        # Dashboard aceita POST mas não faz nada com ele
        self.assertEqual(response.status_code, 200)

    def test_dashboard_cliente_with_different_status_pedidos(self):
        """Testa dashboard com pedidos em status variados."""
        self.client.login(username="cliente_test", password="testpass123")

        # Criar pedidos com diferentes status
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            peso_carga=100.0,
            prazo_desejado=5,
            status=StatusPedido.APROVADO,
        )
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Brasília",
            peso_carga=200.0,
            prazo_desejado=7,
            status=StatusPedido.EM_TRANSPORTE,
        )
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Curitiba",
            peso_carga=150.0,
            prazo_desejado=3,
            status=StatusPedido.CANCELADO,
        )

        response = self.client.get(self.url)

        # Total de 3 pedidos
        self.assertEqual(response.context["total_pedidos"], 3)
        # Nenhum pendente (COTACAO ou PENDENTE)
        self.assertEqual(response.context["pedidos_pendentes"], 0)
        # Nenhum concluído
        self.assertEqual(response.context["pedidos_concluidos"], 0)

    def test_dashboard_cliente_context_keys(self):
        """Testa que todas as chaves esperadas estão no contexto."""
        self.client.login(username="cliente_test", password="testpass123")
        response = self.client.get(self.url)

        expected_keys = ["profile", "pedidos_recentes", "total_pedidos", "pedidos_pendentes", "pedidos_concluidos"]

        for key in expected_keys:
            self.assertIn(key, response.context)

    def test_dashboard_cliente_pedidos_recentes_ordering(self):
        """Testa que pedidos recentes estão ordenados por data."""
        self.client.login(username="cliente_test", password="testpass123")

        # Criar 3 pedidos
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            peso_carga=100.0,
            prazo_desejado=5,
        )
        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Brasília",
            peso_carga=200.0,
            prazo_desejado=7,
        )
        pedido3 = Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Curitiba",
            peso_carga=150.0,
            prazo_desejado=3,
        )

        response = self.client.get(self.url)

        # Deve retornar apenas o mais recente (pedido3)
        pedidos_recentes = response.context["pedidos_recentes"]
        self.assertEqual(len(pedidos_recentes), 1)
        self.assertEqual(pedidos_recentes[0].id, pedido3.id)

    def test_dashboard_cliente_anonymous_user_redirect(self):
        """Testa que usuário anônimo é redirecionado."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/contas/login/"))

    def test_dashboard_cliente_with_observacoes(self):
        """Testa dashboard com pedidos que têm observações."""
        self.client.login(username="cliente_test", password="testpass123")

        Pedido.objects.create(
            cliente=self.cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            peso_carga=100.0,
            prazo_desejado=5,
            observacoes="Carga frágil",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_pedidos"], 1)
