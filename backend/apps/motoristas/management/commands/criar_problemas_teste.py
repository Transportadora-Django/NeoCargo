"""
Comando para criar problemas de entrega de teste
"""

from django.core.management.base import BaseCommand
from apps.pedidos.models import Pedido, StatusPedido
from apps.motoristas.models import Motorista, ProblemaEntrega, StatusProblema, TipoProblema, AtribuicaoPedido
from apps.veiculos.models import Veiculo


class Command(BaseCommand):
    help = "Cria problemas de entrega de teste"

    def handle(self, *args, **kwargs):
        # Busca um motorista existente
        motorista = Motorista.objects.first()
        if not motorista:
            self.stdout.write(self.style.ERROR("❌ Nenhum motorista encontrado. Execute seed_motoristas primeiro."))
            return

        self.stdout.write(self.style.SUCCESS(f"✅ Usando motorista: {motorista.profile.user.get_full_name()}"))

        # Busca um pedido em transporte
        pedidos = Pedido.objects.filter(status=StatusPedido.EM_TRANSPORTE)

        if not pedidos.exists():
            self.stdout.write(
                self.style.ERROR("❌ Nenhum pedido em transporte encontrado. Execute criar_pedidos_teste primeiro.")
            )
            return

        pedido = pedidos.first()

        # Busca ou cria um veículo
        veiculo = Veiculo.objects.first()
        if not veiculo:
            self.stdout.write(self.style.ERROR("❌ Nenhum veículo encontrado. Execute popular_veiculos primeiro."))
            return

        # Cria ou busca atribuição
        atribuicao, created = AtribuicaoPedido.objects.get_or_create(
            pedido=pedido, defaults={"motorista": motorista, "veiculo": veiculo}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Atribuição criada para pedido #{pedido.id}"))

        # Cria problemas de teste
        problemas = [
            {
                "tipo": TipoProblema.ROTA,
                "descricao": "Trânsito intenso na rodovia. Previsão de atraso de 2 horas.",
                "status": StatusProblema.PENDENTE,
            },
            {
                "tipo": TipoProblema.CARGA,
                "descricao": "Dano na embalagem durante transporte. Produto aparentemente intacto.",
                "status": StatusProblema.EM_ANALISE,
            },
            {
                "tipo": TipoProblema.VEICULO,
                "descricao": "Problema mecânico leve no veículo. Aguardando revisão.",
                "status": StatusProblema.PENDENTE,
            },
        ]

        created_count = 0
        for problema_data in problemas:
            # Verifica se já existe
            existe = ProblemaEntrega.objects.filter(
                atribuicao=atribuicao, tipo=problema_data["tipo"], status=problema_data["status"]
            ).exists()

            if not existe:
                ProblemaEntrega.objects.create(atribuicao=atribuicao, **problema_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Problema criado: {problema_data['tipo']} ({problema_data['status']})")
                )

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Total de {created_count} problema(s) criado(s) com sucesso!"))
        else:
            self.stdout.write(
                self.style.WARNING("\n⚠️  Nenhum problema novo foi criado (já existem problemas similares)")
            )
