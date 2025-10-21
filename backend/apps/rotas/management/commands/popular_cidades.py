"""
Comando para popular cidades principais do Brasil com coordenadas.
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.rotas.models import Cidade, Estado


class Command(BaseCommand):
    help = "Popula cidades principais do Brasil com coordenadas"

    def handle(self, *args, **options):
        self.stdout.write("Populando cidades principais do Brasil...")

        # Cidades principais com coordenadas (lat, long)
        cidades = [
            # Região Sudeste
            {
                "nome": "São Paulo",
                "estado": Estado.SP,
                "latitude": Decimal("-23.5505199"),
                "longitude": Decimal("-46.6333094"),
            },
            {
                "nome": "Rio de Janeiro",
                "estado": Estado.RJ,
                "latitude": Decimal("-22.9068467"),
                "longitude": Decimal("-43.1728965"),
            },
            {
                "nome": "Belo Horizonte",
                "estado": Estado.MG,
                "latitude": Decimal("-19.9166813"),
                "longitude": Decimal("-43.9344931"),
            },
            {
                "nome": "Campinas",
                "estado": Estado.SP,
                "latitude": Decimal("-22.9099384"),
                "longitude": Decimal("-47.0626332"),
            },
            {
                "nome": "Santos",
                "estado": Estado.SP,
                "latitude": Decimal("-23.9608647"),
                "longitude": Decimal("-46.3334537"),
            },
            {
                "nome": "Vitória",
                "estado": Estado.ES,
                "latitude": Decimal("-20.3155151"),
                "longitude": Decimal("-40.3128767"),
            },
            # Região Sul
            {
                "nome": "Curitiba",
                "estado": Estado.PR,
                "latitude": Decimal("-25.4284"),
                "longitude": Decimal("-49.2733"),
            },
            {
                "nome": "Porto Alegre",
                "estado": Estado.RS,
                "latitude": Decimal("-30.0346"),
                "longitude": Decimal("-51.2177"),
            },
            {
                "nome": "Florianópolis",
                "estado": Estado.SC,
                "latitude": Decimal("-27.5954"),
                "longitude": Decimal("-48.5480"),
            },
            {
                "nome": "Joinville",
                "estado": Estado.SC,
                "latitude": Decimal("-26.3045"),
                "longitude": Decimal("-48.8487"),
            },
            # Região Centro-Oeste
            {
                "nome": "Brasília",
                "estado": Estado.DF,
                "latitude": Decimal("-15.8267"),
                "longitude": Decimal("-47.9218"),
            },
            {
                "nome": "Goiânia",
                "estado": Estado.GO,
                "latitude": Decimal("-16.6869"),
                "longitude": Decimal("-49.2648"),
            },
            {
                "nome": "Campo Grande",
                "estado": Estado.MS,
                "latitude": Decimal("-20.4697"),
                "longitude": Decimal("-54.6201"),
            },
            {
                "nome": "Cuiabá",
                "estado": Estado.MT,
                "latitude": Decimal("-15.6014"),
                "longitude": Decimal("-56.0979"),
            },
            # Região Nordeste
            {
                "nome": "Salvador",
                "estado": Estado.BA,
                "latitude": Decimal("-12.9714"),
                "longitude": Decimal("-38.5014"),
            },
            {
                "nome": "Fortaleza",
                "estado": Estado.CE,
                "latitude": Decimal("-3.7319"),
                "longitude": Decimal("-38.5267"),
            },
            {
                "nome": "Recife",
                "estado": Estado.PE,
                "latitude": Decimal("-8.0476"),
                "longitude": Decimal("-34.8770"),
            },
            {
                "nome": "Natal",
                "estado": Estado.RN,
                "latitude": Decimal("-5.7945"),
                "longitude": Decimal("-35.2110"),
            },
            {
                "nome": "João Pessoa",
                "estado": Estado.PB,
                "latitude": Decimal("-7.1195"),
                "longitude": Decimal("-34.8450"),
            },
            {
                "nome": "Maceió",
                "estado": Estado.AL,
                "latitude": Decimal("-9.6658"),
                "longitude": Decimal("-35.7353"),
            },
            # Região Norte
            {
                "nome": "Manaus",
                "estado": Estado.AM,
                "latitude": Decimal("-3.1190"),
                "longitude": Decimal("-60.0217"),
            },
            {
                "nome": "Belém",
                "estado": Estado.PA,
                "latitude": Decimal("-1.4558"),
                "longitude": Decimal("-48.5039"),
            },
            {
                "nome": "Porto Velho",
                "estado": Estado.RO,
                "latitude": Decimal("-8.7619"),
                "longitude": Decimal("-63.9039"),
            },
            {
                "nome": "Palmas",
                "estado": Estado.TO,
                "latitude": Decimal("-10.1840"),
                "longitude": Decimal("-48.3336"),
            },
        ]

        created_count = 0
        updated_count = 0

        for cidade_data in cidades:
            cidade, created = Cidade.objects.update_or_create(
                nome=cidade_data["nome"],
                estado=cidade_data["estado"],
                defaults={
                    "latitude": cidade_data["latitude"],
                    "longitude": cidade_data["longitude"],
                    "ativa": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Criada: {cidade.nome_completo}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"→ Atualizada: {cidade.nome_completo}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Processo concluído!\n"
                f"   Cidades criadas: {created_count}\n"
                f"   Cidades atualizadas: {updated_count}\n"
                f"   Total: {created_count + updated_count}"
            )
        )
