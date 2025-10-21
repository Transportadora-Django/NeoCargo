"""
Testes para os models do app Dashboard.
Como o Dashboard não tem models próprios, testa a integração com models de outros apps.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.contas.models import Profile, Role
from apps.pedidos.models import Pedido, StatusPedido

User = get_user_model()


class DashboardModelsIntegrationTest(TestCase):
    """Testes de integração dos models usados pelo Dashboard."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.profile = Profile.objects.get(user=self.user)

    def test_user_profile_relationship(self):
        """Testa relacionamento entre User e Profile."""
        self.assertEqual(self.user.profile, self.profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_default_role(self):
        """Testa que o perfil é criado com role padrão."""
        self.assertIsNotNone(self.profile.role)
        self.assertIn(self.profile.role, [Role.CLIENTE, Role.MOTORISTA, Role.OWNER])

    def test_user_pedidos_relationship(self):
        """Testa relacionamento entre User e Pedidos."""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=100.0,
            prazo_desejado=5,
        )

        self.assertEqual(self.user.pedidos.count(), 1)
        self.assertEqual(self.user.pedidos.first(), pedido)

    def test_pedido_status_choices(self):
        """Testa que os status de pedido estão disponíveis."""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=100.0,
            prazo_desejado=5,
            status=StatusPedido.COTACAO,
        )

        self.assertEqual(pedido.status, StatusPedido.COTACAO)
        self.assertIn(pedido.status, [choice[0] for choice in StatusPedido.choices])

    def test_multiple_pedidos_per_user(self):
        """Testa que um usuário pode ter múltiplos pedidos."""
        for i in range(5):
            Pedido.objects.create(
                cliente=self.user,
                cidade_origem="São Paulo",
                cidade_destino=f"Destino {i}",
                peso_carga=100.0 + i,
                prazo_desejado=5 + i,
            )

        self.assertEqual(self.user.pedidos.count(), 5)

    def test_pedido_ordering(self):
        """Testa ordenação de pedidos por data de criação."""
        Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            peso_carga=100.0,
            prazo_desejado=5,
        )
        pedido2 = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Brasília",
            peso_carga=200.0,
            prazo_desejado=7,
        )

        pedidos = self.user.pedidos.order_by("-created_at")
        self.assertEqual(pedidos.first(), pedido2)  # Mais recente primeiro

    def test_profile_role_update(self):
        """Testa atualização de role do perfil."""
        self.profile.role = Role.MOTORISTA
        self.profile.save()

        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.role, Role.MOTORISTA)

    def test_user_deletion_cascades_to_profile(self):
        """Testa que deletar usuário remove o perfil."""
        user_id = self.user.id
        self.user.delete()

        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Profile.objects.filter(user_id=user_id).exists())

    def test_user_deletion_cascades_to_pedidos(self):
        """Testa que deletar usuário remove seus pedidos."""
        Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            peso_carga=100.0,
            prazo_desejado=5,
        )

        user_id = self.user.id
        self.user.delete()

        self.assertFalse(Pedido.objects.filter(cliente_id=user_id).exists())

    def test_pedido_status_filtering(self):
        """Testa filtragem de pedidos por status."""
        Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            peso_carga=100.0,
            prazo_desejado=5,
            status=StatusPedido.COTACAO,
        )
        Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Brasília",
            peso_carga=200.0,
            prazo_desejado=7,
            status=StatusPedido.CONCLUIDO,
        )

        cotacao_pedidos = Pedido.objects.filter(cliente=self.user, status=StatusPedido.COTACAO)
        concluido_pedidos = Pedido.objects.filter(cliente=self.user, status=StatusPedido.CONCLUIDO)

        self.assertEqual(cotacao_pedidos.count(), 1)
        self.assertEqual(concluido_pedidos.count(), 1)

    def test_pedido_required_fields(self):
        """Testa que campos obrigatórios são validados."""
        from django.core.exceptions import ValidationError

        pedido = Pedido(cliente=self.user)

        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_profile_string_representation(self):
        """Testa representação em string do Profile."""
        profile_str = str(self.profile)
        self.assertIn(self.user.username, profile_str)

    def test_pedido_decimal_precision(self):
        """Testa precisão decimal dos campos de peso e preço."""
        from decimal import Decimal

        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio",
            peso_carga=Decimal("123.45"),
            prazo_desejado=5,
            preco_final=Decimal("1234.56"),
        )

        self.assertEqual(pedido.peso_carga, Decimal("123.45"))
        self.assertEqual(pedido.preco_final, Decimal("1234.56"))
