"""
Comando para criar pedidos de teste
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.pedidos.models import Pedido, StatusPedido, OpcaoCotacao
from apps.contas.models import Profile, Role
from decimal import Decimal


class Command(BaseCommand):
    help = "Cria pedidos de teste com diferentes status"

    def handle(self, *args, **kwargs):
        # Busca ou cria um cliente
        cliente_username = "cliente_teste"
        if not User.objects.filter(username=cliente_username).exists():
            cliente = User.objects.create_user(
                username=cliente_username,
                email="cliente@neocargo.com",
                password="cliente123",
                first_name="Cliente",
                last_name="Teste",
            )
            profile = Profile.objects.get(user=cliente)
            profile.role = Role.CLIENTE
            profile.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Cliente criado: {cliente_username}"))
        else:
            cliente = User.objects.get(username=cliente_username)
            self.stdout.write(self.style.WARNING(f"⚠️  Cliente já existe: {cliente_username}"))

        # Cria pedidos com diferentes status
        pedidos = [
            {
                "cidade_origem": "São Paulo",
                "cidade_destino": "Rio de Janeiro",
                "peso_carga": Decimal("500.00"),
                "prazo_desejado": 3,
                "opcao": OpcaoCotacao.ECONOMICO,
                "status": StatusPedido.PENDENTE,
                "observacoes": "Carga frágil - manuseio cuidadoso",
            },
            {
                "cidade_origem": "Brasília",
                "cidade_destino": "Belo Horizonte",
                "peso_carga": Decimal("1200.00"),
                "prazo_desejado": 5,
                "opcao": OpcaoCotacao.RAPIDO,
                "status": StatusPedido.COTACAO,
                "observacoes": "Entrega urgente",
            },
            {
                "cidade_origem": "Curitiba",
                "cidade_destino": "Porto Alegre",
                "peso_carga": Decimal("800.00"),
                "prazo_desejado": 7,
                "opcao": OpcaoCotacao.CUSTO_BENEFICIO,
                "status": StatusPedido.APROVADO,
                "observacoes": "Material eletrônico",
            },
            {
                "cidade_origem": "Salvador",
                "cidade_destino": "Recife",
                "peso_carga": Decimal("300.00"),
                "prazo_desejado": 4,
                "opcao": OpcaoCotacao.ECONOMICO,
                "status": StatusPedido.EM_TRANSPORTE,
                "observacoes": "Documentos importantes",
            },
        ]

        created_count = 0
        for pedido_data in pedidos:
            # Verifica se já existe um pedido similar
            existe = Pedido.objects.filter(
                cliente=cliente,
                cidade_origem=pedido_data["cidade_origem"],
                cidade_destino=pedido_data["cidade_destino"],
                status=pedido_data["status"],
            ).exists()

            if not existe:
                Pedido.objects.create(cliente=cliente, **pedido_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Pedido criado: {pedido_data['cidade_origem']} → "
                        f"{pedido_data['cidade_destino']} ({pedido_data['status']})"
                    )
                )

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Total de {created_count} pedido(s) criado(s) com sucesso!"))
        else:
            self.stdout.write(self.style.WARNING("\n⚠️  Nenhum pedido novo foi criado (já existem pedidos similares)"))
