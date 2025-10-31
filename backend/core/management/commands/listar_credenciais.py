"""
Comando para listar credenciais de teste
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.pedidos.models import Pedido
from apps.motoristas.models import ProblemaEntrega


class Command(BaseCommand):
    help = "Lista credenciais de teste disponíveis"

    def handle(self, *args, **kwargs):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🔐 CREDENCIAIS DE TESTE - NEOCARGO"))
        self.stdout.write("=" * 60)

        # Gerente
        self.stdout.write("\n" + self.style.HTTP_INFO("📊 GERENTE:"))
        self.stdout.write("   URL: http://localhost:8000/contas/login/")
        self.stdout.write("   Username: gerente")
        self.stdout.write("   Senha: gerente123")
        self.stdout.write("   Dashboard: /gestao/gerente/dashboard/")

        # Dono
        dono = User.objects.filter(profile__role="owner").first()
        if dono:
            self.stdout.write("\n" + self.style.HTTP_INFO("👔 DONO (Owner):"))
            self.stdout.write(f"   Username: {dono.username}")
            self.stdout.write("   Dashboard: /gestao/dashboard/")

        # Cliente
        cliente = User.objects.filter(username="cliente_teste").first()
        if cliente:
            self.stdout.write("\n" + self.style.HTTP_INFO("🛒 CLIENTE:"))
            self.stdout.write("   Username: cliente_teste")
            self.stdout.write("   Senha: cliente123")
            self.stdout.write("   Dashboard: /pedidos/")

        # Motorista
        motorista_user = User.objects.filter(profile__role="motorista").first()
        if motorista_user:
            self.stdout.write("\n" + self.style.HTTP_INFO("🚚 MOTORISTA:"))
            self.stdout.write(f"   Username: {motorista_user.username}")
            self.stdout.write("   Dashboard: /motoristas/dashboard/")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📦 DADOS DE TESTE"))
        self.stdout.write("=" * 60)

        # Pedidos
        total_pedidos = Pedido.objects.count()
        pedidos_pendentes = Pedido.objects.filter(status="pendente").count()
        self.stdout.write(f"\n✅ {total_pedidos} pedidos no sistema")
        self.stdout.write(f"   - {pedidos_pendentes} pedidos pendentes de aprovação")

        # Problemas
        total_problemas = ProblemaEntrega.objects.count()
        problemas_pendentes = ProblemaEntrega.objects.filter(status="pendente").count()
        self.stdout.write(f"\n⚠️  {total_problemas} problemas reportados")
        self.stdout.write(f"   - {problemas_pendentes} problemas pendentes")

        self.stdout.write("\n" + "=" * 60 + "\n")
