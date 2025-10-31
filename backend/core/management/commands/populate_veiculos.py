"""
Comando para popular especificações de veículos e veículos iniciais.
Usado no deploy para garantir dados básicos no sistema.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.veiculos.models import EspecificacaoVeiculo, Veiculo


class Command(BaseCommand):
    help = "Popula especificações de veículos e veículos iniciais no sistema"

    def handle(self, *args, **options):
        self.stdout.write("🚚 Populando especificações de veículos...")

        try:
            with transaction.atomic():
                # Verificar se já existem especificações
                espec_count = EspecificacaoVeiculo.objects.count()
                self.stdout.write(f"📊 Especificações existentes: {espec_count}")

                if espec_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {espec_count} especificações já existem. Pulando população...")
                    )
                    return

                # Criar especificações de veículos
                especificacoes_data = [
                    {
                        "tipo": "van",
                        "carga_maxima": 1500,
                        "combustivel_principal": "gasolina",
                        "rendimento_principal": 8.5,
                        "combustivel_alternativo": "alcool",
                        "rendimento_alternativo": 6.0,
                        "velocidade_media": 80,
                        "reducao_rendimento_principal": 0.0001,
                        "reducao_rendimento_alternativo": 0.0001,
                    },
                    {
                        "tipo": "carreta",
                        "carga_maxima": 30000,
                        "combustivel_principal": "diesel",
                        "rendimento_principal": 3.5,
                        "velocidade_media": 70,
                        "reducao_rendimento_principal": 0.00005,
                    },
                    {
                        "tipo": "carro",
                        "carga_maxima": 500,
                        "combustivel_principal": "gasolina",
                        "rendimento_principal": 12.0,
                        "combustivel_alternativo": "alcool",
                        "rendimento_alternativo": 8.5,
                        "velocidade_media": 90,
                        "reducao_rendimento_principal": 0.0002,
                        "reducao_rendimento_alternativo": 0.0002,
                    },
                    {
                        "tipo": "moto",
                        "carga_maxima": 50,
                        "combustivel_principal": "gasolina",
                        "rendimento_principal": 35.0,
                        "velocidade_media": 60,
                        "reducao_rendimento_principal": 0.0005,
                    },
                ]

                especificacoes = {}
                for espec_data in especificacoes_data:
                    espec = EspecificacaoVeiculo.objects.create(**espec_data)
                    especificacoes[espec.tipo] = espec
                    self.stdout.write(
                        f"  ✓ Especificação criada: {espec.get_tipo_display()} "
                        f"({espec.carga_maxima}kg, {espec.rendimento_principal}km/l)"
                    )

                self.stdout.write(self.style.SUCCESS(f"✅ {len(especificacoes)} especificações criadas com sucesso!"))

                # Criar veículos de exemplo
                veiculos_data = [
                    {
                        "placa": "ABC-1234",
                        "marca": "Mercedes-Benz",
                        "modelo": "Sprinter",
                        "ano": 2022,
                        "cor": "Branco",
                        "especificacao": "van",
                    },
                    {
                        "placa": "DEF-5678",
                        "marca": "Volvo",
                        "modelo": "FH 540",
                        "ano": 2023,
                        "cor": "Azul",
                        "especificacao": "carreta",
                    },
                    {
                        "placa": "GHI-9012",
                        "marca": "Fiat",
                        "modelo": "Uno",
                        "ano": 2020,
                        "cor": "Prata",
                        "especificacao": "carro",
                    },
                    {
                        "placa": "JKL-3456",
                        "marca": "Honda",
                        "modelo": "CG 160",
                        "ano": 2022,
                        "cor": "Vermelho",
                        "especificacao": "moto",
                    },
                ]

                veiculos_criados = 0
                for veiculo_data in veiculos_data:
                    espec_tipo = veiculo_data.pop("especificacao")
                    if espec_tipo in especificacoes:
                        veiculo = Veiculo.objects.create(especificacao=especificacoes[espec_tipo], **veiculo_data)
                        veiculos_criados += 1
                        self.stdout.write(
                            f"  ✓ Veículo criado: {veiculo.placa} - "
                            f"{veiculo.marca} {veiculo.modelo} ({veiculo.especificacao.tipo})"
                        )

                self.stdout.write(self.style.SUCCESS(f"✅ {veiculos_criados} veículos criados com sucesso!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao popular veículos: {str(e)}"))
            raise
