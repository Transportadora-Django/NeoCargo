from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from apps.pedidos.models import Pedido, StatusPedido


class IntegracaoTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", email="user1@example.com", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", email="user2@example.com", password="testpass123")

    def test_fluxo_completo_pedido(self):
        """Testa fluxo completo de pedido"""
        # 1. Criar pedido
        pedido = Pedido.objects.create(
            cliente=self.user1,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
            observacoes="Carga frágil",
        )

        # 2. Verificar status inicial
        self.assertEqual(pedido.status, StatusPedido.PENDENTE)
        self.assertTrue(pedido.is_pendente)
        self.assertTrue(pedido.pode_ser_cancelado())

        # 3. Tentar cancelar (deve funcionar)
        result = pedido.cancelar()
        self.assertTrue(result)
        self.assertEqual(pedido.status, StatusPedido.CANCELADO)
        self.assertTrue(pedido.is_cancelado)
        self.assertFalse(pedido.pode_ser_cancelado())

    def test_isolamento_entre_usuarios(self):
        """Testa que usuários só veem seus próprios pedidos"""
        # Criar pedidos para cada usuário
        pedido1 = Pedido.objects.create(
            cliente=self.user1,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
        )

        pedido2 = Pedido.objects.create(
            cliente=self.user2,
            cidade_origem="Campinas",
            cidade_destino="Santos",
            peso_carga=Decimal("50.00"),
            prazo_desejado=5,
        )

        # Verificar isolamento
        pedidos_user1 = Pedido.objects.filter(cliente=self.user1)
        pedidos_user2 = Pedido.objects.filter(cliente=self.user2)

        self.assertEqual(pedidos_user1.count(), 1)
        self.assertEqual(pedidos_user2.count(), 1)
        self.assertEqual(pedidos_user1.first(), pedido1)
        self.assertEqual(pedidos_user2.first(), pedido2)

    def test_multiplos_pedidos_mesmo_usuario(self):
        """Testa múltiplos pedidos do mesmo usuário"""
        pedidos_data = [
            {
                "cidade_origem": "São Paulo",
                "cidade_destino": "Rio de Janeiro",
                "peso_carga": Decimal("100.00"),
                "prazo_desejado": 7,
            },
            {
                "cidade_origem": "Campinas",
                "cidade_destino": "Santos",
                "peso_carga": Decimal("50.00"),
                "prazo_desejado": 5,
            },
            {
                "cidade_origem": "Ribeirão Preto",
                "cidade_destino": "Campinas",
                "peso_carga": Decimal("75.00"),
                "prazo_desejado": 3,
            },
        ]

        pedidos_criados = []
        for data in pedidos_data:
            pedido = Pedido.objects.create(cliente=self.user1, **data)
            pedidos_criados.append(pedido)

        # Verificar que todos foram criados
        self.assertEqual(Pedido.objects.filter(cliente=self.user1).count(), 3)

        # Verificar ordenação (mais recente primeiro)
        pedidos_ordenados = Pedido.objects.filter(cliente=self.user1).order_by("-created_at")
        self.assertEqual(list(pedidos_ordenados), list(reversed(pedidos_criados)))

    def test_estados_diferentes_pedidos(self):
        """Testa pedidos em diferentes estados"""
        # Pedido pendente
        pedido_pendente = Pedido.objects.create(
            cliente=self.user1,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("100.00"),
            prazo_desejado=7,
            status=StatusPedido.PENDENTE,
        )

        # Pedido aprovado
        pedido_aprovado = Pedido.objects.create(
            cliente=self.user1,
            cidade_origem="Campinas",
            cidade_destino="Santos",
            peso_carga=Decimal("50.00"),
            prazo_desejado=5,
            status=StatusPedido.APROVADO,
        )

        # Pedido cancelado
        pedido_cancelado = Pedido.objects.create(
            cliente=self.user1,
            cidade_origem="Ribeirão Preto",
            cidade_destino="Campinas",
            peso_carga=Decimal("75.00"),
            prazo_desejado=3,
            status=StatusPedido.CANCELADO,
        )

        # Verificar propriedades de cada um
        self.assertTrue(pedido_pendente.is_pendente)
        self.assertTrue(pedido_pendente.pode_ser_cancelado())

        self.assertFalse(pedido_aprovado.is_pendente)
        self.assertFalse(pedido_aprovado.pode_ser_cancelado())

        self.assertTrue(pedido_cancelado.is_cancelado)
        self.assertFalse(pedido_cancelado.pode_ser_cancelado())
