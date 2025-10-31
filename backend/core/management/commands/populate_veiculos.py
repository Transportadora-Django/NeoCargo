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
                if EspecificacaoVeiculo.objects.exists():
                    self.stdout.write(self.style.WARNING("⚠️  Especificações já existem. Pulando população..."))
                    return

                # Criar especificações de veículos
                especificacoes_data = [
                    {
                        "tipo": "Van",
                        "capacidade_kg": 1500,
                        "tipo_combustivel_principal": "gasolina",
                        "rendimento_combustivel_principal": 8.5,
                        "tipo_combustivel_alternativo": "gnv",
                        "rendimento_combustivel_alternativo": 12.0,
                    },
                    {
                        "tipo": "Caminhão 3/4",
                        "capacidade_kg": 3500,
                        "tipo_combustivel_principal": "diesel",
                        "rendimento_combustivel_principal": 6.5,
                    },
                    {
                        "tipo": "Caminhão Toco",
                        "capacidade_kg": 6000,
                        "tipo_combustivel_principal": "diesel",
                        "rendimento_combustivel_principal": 5.0,
                    },
                    {
                        "tipo": "Caminhão Truck",
                        "capacidade_kg": 14000,
                        "tipo_combustivel_principal": "diesel",
                        "rendimento_combustivel_principal": 4.0,
                    },
                    {
                        "tipo": "Carreta",
                        "capacidade_kg": 30000,
                        "tipo_combustivel_principal": "diesel",
                        "rendimento_combustivel_principal": 3.5,
                    },
                    {
                        "tipo": "Bitrem",
                        "capacidade_kg": 45000,
                        "tipo_combustivel_principal": "diesel",
                        "rendimento_combustivel_principal": 3.0,
                    },
                ]

                especificacoes = {}
                for espec_data in especificacoes_data:
                    espec = EspecificacaoVeiculo.objects.create(**espec_data)
                    especificacoes[espec.tipo] = espec
                    self.stdout.write(
                        f"  ✓ Especificação criada: {espec.tipo} "
                        f"({espec.capacidade_kg}kg, {espec.rendimento_combustivel_principal}km/l)"
                    )

                self.stdout.write(self.style.SUCCESS(f"✅ {len(especificacoes)} especificações criadas com sucesso!"))

                # Criar veículos de exemplo
                veiculos_data = [
                    {
                        "placa": "ABC-1234",
                        "marca": "Mercedes-Benz",
                        "modelo": "Sprinter",
                        "ano": 2022,
                        "especificacao": "Van",
                    },
                    {
                        "placa": "DEF-5678",
                        "marca": "Ford",
                        "modelo": "Cargo 816",
                        "ano": 2021,
                        "especificacao": "Caminhão 3/4",
                    },
                    {
                        "placa": "GHI-9012",
                        "marca": "Volkswagen",
                        "modelo": "Delivery 11.180",
                        "ano": 2023,
                        "especificacao": "Caminhão Toco",
                    },
                    {
                        "placa": "JKL-3456",
                        "marca": "Scania",
                        "modelo": "P 320",
                        "ano": 2022,
                        "especificacao": "Caminhão Truck",
                    },
                    {
                        "placa": "MNO-7890",
                        "marca": "Volvo",
                        "modelo": "FH 540",
                        "ano": 2023,
                        "especificacao": "Carreta",
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
