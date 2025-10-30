"""
Comando para popular especificações de veículos baseadas nas regras do Zé do Caminhão.
"""

from django.core.management.base import BaseCommand
from apps.veiculos.models import EspecificacaoVeiculo, TipoVeiculo, TipoCombustivel


class Command(BaseCommand):
    help = "Popula especificações de veículos baseadas nas regras do Zé do Caminhão"

    def handle(self, *args, **options):
        self.stdout.write("Populando especificações de veículos...")

        especificacoes = [
            {
                "tipo": TipoVeiculo.CARRETA,
                "combustivel_principal": TipoCombustivel.DIESEL,
                "combustivel_alternativo": None,
                "rendimento_principal": 8.0,
                "rendimento_alternativo": None,
                "carga_maxima": 30000.0,  # 30 toneladas em kg
                "velocidade_media": 60,
                "reducao_rendimento_principal": 0.0002,
                "reducao_rendimento_alternativo": None,
            },
            {
                "tipo": TipoVeiculo.VAN,
                "combustivel_principal": TipoCombustivel.DIESEL,
                "combustivel_alternativo": None,
                "rendimento_principal": 10.0,
                "rendimento_alternativo": None,
                "carga_maxima": 3500.0,  # 3.5 toneladas em kg
                "velocidade_media": 80,
                "reducao_rendimento_principal": 0.001,
                "reducao_rendimento_alternativo": None,
            },
            {
                "tipo": TipoVeiculo.CARRO,
                "combustivel_principal": TipoCombustivel.GASOLINA,
                "combustivel_alternativo": TipoCombustivel.ALCOOL,
                "rendimento_principal": 14.0,
                "rendimento_alternativo": 12.0,
                "carga_maxima": 360.0,  # 360 kg
                "velocidade_media": 100,
                "reducao_rendimento_principal": 0.025,
                "reducao_rendimento_alternativo": 0.0231,
            },
            {
                "tipo": TipoVeiculo.MOTO,
                "combustivel_principal": TipoCombustivel.GASOLINA,
                "combustivel_alternativo": TipoCombustivel.ALCOOL,
                "rendimento_principal": 50.0,
                "rendimento_alternativo": 43.0,
                "carga_maxima": 50.0,  # 50 kg
                "velocidade_media": 110,
                "reducao_rendimento_principal": 0.3,
                "reducao_rendimento_alternativo": 0.4,
            },
        ]

        for espec_data in especificacoes:
            espec, created = EspecificacaoVeiculo.objects.update_or_create(tipo=espec_data["tipo"], defaults=espec_data)

            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Criada especificação: {espec.get_tipo_display()}"))
            else:
                self.stdout.write(self.style.WARNING(f"→ Atualizada especificação: {espec.get_tipo_display()}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Especificações de veículos populadas com sucesso!"))
