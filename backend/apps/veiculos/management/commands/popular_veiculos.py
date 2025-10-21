"""
Comando para popular veículos de exemplo para testes.
"""

from django.core.management.base import BaseCommand
from apps.veiculos.models import Veiculo, EspecificacaoVeiculo, TipoVeiculo


class Command(BaseCommand):
    help = "Popula veículos de exemplo para testes"

    def handle(self, *args, **options):
        self.stdout.write("Populando veículos de exemplo...")

        # Buscar especificações
        try:
            espec_carreta = EspecificacaoVeiculo.objects.get(tipo=TipoVeiculo.CARRETA)
            espec_van = EspecificacaoVeiculo.objects.get(tipo=TipoVeiculo.VAN)
            espec_carro = EspecificacaoVeiculo.objects.get(tipo=TipoVeiculo.CARRO)
            espec_moto = EspecificacaoVeiculo.objects.get(tipo=TipoVeiculo.MOTO)
        except EspecificacaoVeiculo.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Especificações não encontradas. "
                    "Execute 'python manage.py popular_especificacoes' primeiro."
                )
            )
            return

        veiculos = [
            # Carretas
            {
                "especificacao": espec_carreta,
                "marca": "Scania",
                "modelo": "R450",
                "placa": "ABC1234",
                "ano": 2022,
                "cor": "Branco",
            },
            {
                "especificacao": espec_carreta,
                "marca": "Volvo",
                "modelo": "FH 540",
                "placa": "DEF5678",
                "ano": 2021,
                "cor": "Azul",
            },
            {
                "especificacao": espec_carreta,
                "marca": "Mercedes-Benz",
                "modelo": "Actros 2651",
                "placa": "GHI9012",
                "ano": 2023,
                "cor": "Prata",
            },
            # Vans
            {
                "especificacao": espec_van,
                "marca": "Ford",
                "modelo": "Transit",
                "placa": "JKL3456",
                "ano": 2022,
                "cor": "Branco",
            },
            {
                "especificacao": espec_van,
                "marca": "Renault",
                "modelo": "Master",
                "placa": "MNO7890",
                "ano": 2021,
                "cor": "Cinza",
            },
            {
                "especificacao": espec_van,
                "marca": "Fiat",
                "modelo": "Ducato",
                "placa": "PQR1234",
                "ano": 2023,
                "cor": "Branco",
            },
            # Carros
            {
                "especificacao": espec_carro,
                "marca": "Fiat",
                "modelo": "Strada",
                "placa": "STU5678",
                "ano": 2022,
                "cor": "Vermelho",
            },
            {
                "especificacao": espec_carro,
                "marca": "Volkswagen",
                "modelo": "Saveiro",
                "placa": "VWX9012",
                "ano": 2021,
                "cor": "Branco",
            },
            # Motos
            {
                "especificacao": espec_moto,
                "marca": "Honda",
                "modelo": "CG 160",
                "placa": "YZA3456",
                "ano": 2022,
                "cor": "Preto",
            },
            {
                "especificacao": espec_moto,
                "marca": "Yamaha",
                "modelo": "Factor 150",
                "placa": "BCD7890",
                "ano": 2021,
                "cor": "Azul",
            },
        ]

        created_count = 0
        updated_count = 0

        for veiculo_data in veiculos:
            veiculo, created = Veiculo.objects.update_or_create(
                placa=veiculo_data["placa"],
                defaults={
                    "especificacao": veiculo_data["especificacao"],
                    "marca": veiculo_data["marca"],
                    "modelo": veiculo_data["modelo"],
                    "ano": veiculo_data["ano"],
                    "cor": veiculo_data["cor"],
                    "ativo": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Criado: {veiculo.marca} {veiculo.modelo} - {veiculo.placa}")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"→ Atualizado: {veiculo.marca} {veiculo.modelo} - {veiculo.placa}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Processo concluído!\n"
                f"   Veículos criados: {created_count}\n"
                f"   Veículos atualizados: {updated_count}\n"
                f"   Total: {created_count + updated_count}"
            )
        )
