from django.core.management.base import BaseCommand
from apps.gestao.models import EspecificacaoVeiculo, TipoVeiculo, TipoCombustivel


class Command(BaseCommand):
    help = "Popula as especificações de veículos no banco de dados"

    def handle(self, *args, **options):
        especificacoes = [
            {
                "tipo": TipoVeiculo.CARRETA,
                "combustivel_principal": TipoCombustivel.DIESEL,
                "combustivel_alternativo": None,
                "rendimento_principal": 8.0,
                "rendimento_alternativo": None,
                "carga_maxima": 30000.0,  # 30 toneladas em Kg
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
                "carga_maxima": 3500.0,  # 3,5 toneladas em Kg
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
                "carga_maxima": 360.0,
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
                "carga_maxima": 50.0,
                "velocidade_media": 110,
                "reducao_rendimento_principal": 0.3,
                "reducao_rendimento_alternativo": 0.4,
            },
        ]

        for spec_data in especificacoes:
            especificacao, created = EspecificacaoVeiculo.objects.get_or_create(
                tipo=spec_data["tipo"], defaults=spec_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Criada especificação para {especificacao.get_tipo_display()}"))
            else:
                # Atualiza os dados se já existe
                for key, value in spec_data.items():
                    setattr(especificacao, key, value)
                especificacao.save()
                self.stdout.write(
                    self.style.WARNING(f"Atualizada especificação para {especificacao.get_tipo_display()}")
                )

        self.stdout.write(self.style.SUCCESS("Especificações de veículos configuradas com sucesso!"))
