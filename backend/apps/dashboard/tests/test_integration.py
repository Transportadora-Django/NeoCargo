"""
Testes de integração para o app Dashboard.
Testa o fluxo completo de interação entre dashboard, pedidos e perfis.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.contas.models import Profile, Role
from apps.pedidos.models import Pedido, StatusPedido

User = get_user_model()


class DashboardIntegrationTest(TestCase):
    """Testes de integração do Dashboard."""

    def setUp(self):
        """Configuração inicial para os testes de integração."""
        self.client = Client()

        # Criar usuários de diferentes tipos
        self.cliente = User.objects.create_user(
            username="cliente_integration", email="cliente@integration.com", password="testpass123"
        )
        self.cliente_profile = Profile.objects.get(user=self.cliente)
        self.cliente_profile.role = Role.CLIENTE
        self.cliente_profile.save()

        self.motorista = User.objects.create_user(
            username="motorista_integration", email="motorista@integration.com", password="testpass123"
        )
        self.motorista_profile = Profile.objects.get(user=self.motorista)
        self.motorista_profile.role = Role.MOTORISTA
        self.motorista_profile.save()

        self.owner = User.objects.create_user(
            username="owner_integration", email="owner@integration.com", password="testpass123"
        )
        self.owner_profile = Profile.objects.get(user=self.owner)
        self.owner_profile.role = Role.OWNER
        self.owner_profile.save()

    def test_complete_user_journey_cliente(self):
        """Testa jornada completa do cliente: login → dashboard → visualizar pedidos."""
        # 1. Login
        login_success = self.client.login(username="cliente_integration", password="testpass123")
        self.assertTrue(login_success)

        # 2. Criar pedidos
        Pedido.objects.create(
            cliente=self.cliente,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            observacoes="Eletrônicos",
            peso_carga=500.0,
            prazo_desejado=5,
            status=StatusPedido.COTACAO,
        )
        pedido2 = Pedido.objects.create(
            cliente=self.cliente,
            cidade_origem="São Paulo",
            cidade_destino="Brasília",
            observacoes="Documentos",
            peso_carga=10.0,
            prazo_desejado=3,
            status=StatusPedido.CONCLUIDO,
        )

        # 3. Acessar dashboard
        response = self.client.get(reverse("dashboard:cliente"))
        self.assertEqual(response.status_code, 200)

        # 4. Verificar estatísticas
        self.assertEqual(response.context["total_pedidos"], 2)
        self.assertEqual(response.context["pedidos_pendentes"], 1)
        self.assertEqual(response.context["pedidos_concluidos"], 1)

        # 5. Verificar pedido mais recente
        pedidos_recentes = response.context["pedidos_recentes"]
        self.assertEqual(len(pedidos_recentes), 1)
        self.assertEqual(pedidos_recentes[0].id, pedido2.id)  # Mais recente

    def test_role_based_dashboard_access(self):
        """Testa acesso ao dashboard baseado em roles."""
        # Cliente deve acessar dashboard cliente
        self.client.login(username="cliente_integration", password="testpass123")
        response = self.client.get(reverse("dashboard:cliente"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/cliente.html")

        # Owner deve ser redirecionado
        self.client.logout()
        self.client.login(username="owner_integration", password="testpass123")
        response = self.client.get(reverse("dashboard:cliente"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gestao:dashboard_dono"))

    def test_dashboard_with_multiple_status_pedidos(self):
        """Testa dashboard com pedidos em diferentes status."""
        self.client.login(username="cliente_integration", password="testpass123")

        # Criar pedidos em todos os status possíveis
        status_list = [
            StatusPedido.COTACAO,
            StatusPedido.PENDENTE,
            StatusPedido.APROVADO,
            StatusPedido.EM_TRANSPORTE,
            StatusPedido.CONCLUIDO,
            StatusPedido.CANCELADO,
        ]

        for status in status_list:
            Pedido.objects.create(
                cliente=self.cliente,
                cidade_origem="São Paulo",
                cidade_destino=f"Destino {status}",
                observacoes=f"Carga {status}",
                peso_carga=100.0,
                prazo_desejado=5,
                status=status,
            )

        response = self.client.get(reverse("dashboard:cliente"))

        # Verificar contagens
        self.assertEqual(response.context["total_pedidos"], 6)
        # Pendentes: COTACAO + PENDENTE = 2
        self.assertEqual(response.context["pedidos_pendentes"], 2)
        # Concluídos: apenas CONCLUIDO = 1
        self.assertEqual(response.context["pedidos_concluidos"], 1)

    def test_dashboard_isolation_between_users(self):
        """Testa isolamento de dados entre diferentes usuários."""
        # Criar outro cliente
        outro_cliente = User.objects.create_user(
            username="outro_cliente", email="outro@test.com", password="testpass123"
        )
        outro_profile = Profile.objects.get(user=outro_cliente)
        outro_profile.role = Role.CLIENTE
        outro_profile.save()

        # Criar pedidos para cada cliente
        Pedido.objects.create(
            cliente=self.cliente,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            observacoes="Cliente 1",
            peso_carga=100.0,
            prazo_desejado=5,
            status=StatusPedido.COTACAO,
        )
        Pedido.objects.create(
            cliente=outro_cliente,
            cidade_origem="São Paulo",
            cidade_destino="Brasília",
            observacoes="Cliente 2",
            peso_carga=200.0,
            prazo_desejado=7,
            status=StatusPedido.COTACAO,
        )

        # Login como primeiro cliente
        self.client.login(username="cliente_integration", password="testpass123")
        response = self.client.get(reverse("dashboard:cliente"))

        # Deve ver apenas seus próprios pedidos
        self.assertEqual(response.context["total_pedidos"], 1)
        pedidos = response.context["pedidos_recentes"]
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(pedidos[0].cliente, self.cliente)

    def test_dashboard_performance_with_many_pedidos(self):
        """Testa performance do dashboard com muitos pedidos."""
        self.client.login(username="cliente_integration", password="testpass123")

        # Criar 100 pedidos
        pedidos = []
        for i in range(100):
            pedidos.append(
                Pedido(
                    cliente=self.cliente,
                    cidade_origem="São Paulo",
                    cidade_destino=f"Destino {i}",
                    observacoes=f"Carga {i}",
                    peso_carga=100.0 + i,
                    prazo_desejado=5 + (i % 10),
                    status=StatusPedido.COTACAO if i % 2 == 0 else StatusPedido.CONCLUIDO,
                )
            )
        Pedido.objects.bulk_create(pedidos)

        # Acessar dashboard
        response = self.client.get(reverse("dashboard:cliente"))

        # Verificar que funciona corretamente
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_pedidos"], 100)
        # Apenas 1 pedido recente deve ser retornado
        self.assertEqual(len(response.context["pedidos_recentes"]), 1)

    def test_dashboard_after_profile_update(self):
        """Testa dashboard após atualização de perfil."""
        self.client.login(username="cliente_integration", password="testpass123")

        # Acessar dashboard inicial
        response = self.client.get(reverse("dashboard:cliente"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"].role, Role.CLIENTE)

        # Atualizar role para motorista
        self.cliente_profile.role = Role.MOTORISTA
        self.cliente_profile.save()

        # Acessar dashboard novamente
        response = self.client.get(reverse("dashboard:cliente"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"].role, Role.MOTORISTA)

    def test_dashboard_navigation_flow(self):
        """Testa fluxo de navegação do dashboard."""
        self.client.login(username="cliente_integration", password="testpass123")

        # 1. Acessar dashboard
        response = self.client.get(reverse("dashboard:cliente"))
        self.assertEqual(response.status_code, 200)

        # 2. Verificar que pode acessar outras páginas
        # (assumindo que existem links no dashboard)
        response = self.client.get(reverse("pedidos:criar"))
        self.assertEqual(response.status_code, 200)

        # 3. Voltar ao dashboard
        response = self.client.get(reverse("dashboard:cliente"))
        self.assertEqual(response.status_code, 200)
