from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from apps.pedidos.models import Pedido, StatusPedido


class PedidoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_criar_pedido_basico(self):
        """Testa criação básica de pedido"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
        )

        self.assertEqual(pedido.cliente, self.user)
        self.assertEqual(pedido.cidade_origem, "São Paulo")
        self.assertEqual(pedido.cidade_destino, "Rio de Janeiro")
        self.assertEqual(pedido.peso_carga, Decimal("100.00"))
        self.assertEqual(pedido.prazo_desejado, 7)
        self.assertEqual(pedido.status, StatusPedido.COTACAO)
        self.assertTrue(pedido.is_cotacao)

    def test_pedido_com_observacoes(self):
        """Testa pedido com observações"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="Campinas",
            cidade_destino="Santos",
            peso_carga=Decimal("50.00"),
            prazo_desejado=5,
            observacoes="Mercadoria frágil",
        )

        self.assertEqual(pedido.observacoes, "Mercadoria frágil")

    def test_pode_cancelar_pedido_pendente(self):
        """Testa se pedido pendente pode ser cancelado"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
            status=StatusPedido.PENDENTE,
        )

        self.assertTrue(pedido.pode_ser_cancelado())

        # Cancelar pedido
        result = pedido.cancelar()
        self.assertTrue(result)
        self.assertEqual(pedido.status, StatusPedido.CANCELADO)
        self.assertTrue(pedido.is_cancelado)

    def test_nao_pode_cancelar_pedido_aprovado(self):
        """Testa que pedido aprovado não pode ser cancelado"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
            status=StatusPedido.APROVADO,
        )

        self.assertFalse(pedido.pode_ser_cancelado())

        # Tentar cancelar
        result = pedido.cancelar()
        self.assertFalse(result)
        self.assertEqual(pedido.status, StatusPedido.APROVADO)  # Status não muda

    def test_str_method(self):
        """Testa método __str__ do modelo"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
        )

        expected = f"Pedido #{pedido.id} - {self.user.username} (Cotação Gerada)"
        self.assertEqual(str(pedido), expected)
