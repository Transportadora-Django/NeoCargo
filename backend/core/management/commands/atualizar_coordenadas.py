"""
Comando para atualizar coordenadas de cidades existentes.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.rotas.models import Cidade


class Command(BaseCommand):
    help = "Atualiza coordenadas de cidades existentes"

    def handle(self, *args, **options):
        self.stdout.write("🗺️  Atualizando coordenadas das cidades...")

        # Mapa de coordenadas
        coordenadas = {
            ("São Paulo", "SP"): ("-23.5505199", "-46.6333094"),
            ("Campinas", "SP"): ("-22.9099384", "-47.0626332"),
            ("Santos", "SP"): ("-23.9608647", "-46.3334537"),
            ("São José dos Campos", "SP"): ("-23.1790943", "-45.8869436"),
            ("Ribeirão Preto", "SP"): ("-21.1704844", "-47.8102816"),
            ("Rio de Janeiro", "RJ"): ("-22.9068467", "-43.1728965"),
            ("Niterói", "RJ"): ("-22.8838181", "-43.1030647"),
            ("Campos dos Goytacazes", "RJ"): ("-21.7621661", "-41.3194584"),
            ("Belo Horizonte", "MG"): ("-19.9166813", "-43.9344931"),
            ("Uberlândia", "MG"): ("-18.9188149", "-48.2766837"),
            ("Juiz de Fora", "MG"): ("-21.7641783", "-43.3509286"),
            ("Vitória", "ES"): ("-20.3155151", "-40.3128767"),
            ("Vila Velha", "ES"): ("-20.3298826", "-40.2925124"),
            ("Salvador", "BA"): ("-12.9714", "-38.5014"),
            ("Feira de Santana", "BA"): ("-12.2664", "-38.9663"),
            ("Curitiba", "PR"): ("-25.4284", "-49.2733"),
            ("Londrina", "PR"): ("-23.3045", "-51.1696"),
            ("Maringá", "PR"): ("-23.4209", "-51.9333"),
            ("Florianópolis", "SC"): ("-27.5954", "-48.5480"),
            ("Joinville", "SC"): ("-26.3045", "-48.8487"),
            ("Blumenau", "SC"): ("-26.9194", "-49.0661"),
            ("Porto Alegre", "RS"): ("-30.0346", "-51.2177"),
            ("Caxias do Sul", "RS"): ("-29.1634", "-51.1797"),
            ("Brasília", "DF"): ("-15.8267", "-47.9218"),
            ("Goiânia", "GO"): ("-16.6869", "-49.2648"),
            ("Recife", "PE"): ("-8.0476", "-34.8770"),
            ("Fortaleza", "CE"): ("-3.7319", "-38.5267"),
        }

        atualizadas = 0
        nao_encontradas = 0

        for (nome, estado), (lat, lng) in coordenadas.items():
            try:
                cidade = Cidade.objects.get(nome=nome, estado=estado)
                cidade.latitude = Decimal(lat)
                cidade.longitude = Decimal(lng)
                cidade.save()
                atualizadas += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Atualizada: {cidade.nome_completo} ({lat}, {lng})"))
            except Cidade.DoesNotExist:
                nao_encontradas += 1
                self.stdout.write(self.style.WARNING(f"⚠️  Cidade não encontrada: {nome}/{estado}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Processo concluído!\n"
                f"   Cidades atualizadas: {atualizadas}\n"
                f"   Cidades não encontradas: {nao_encontradas}"
            )
        )
