"""
Comando para popular rotas de exemplo entre as principais cidades.
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.rotas.models import Cidade, Rota, Estado


class Command(BaseCommand):
    help = "Popula rotas de exemplo entre as principais cidades"

    def handle(self, *args, **options):
        self.stdout.write("Populando rotas de exemplo...")

        # Rotas principais (distância em km, tempo estimado em horas, pedágio em R$)
        rotas_data = [
            # Sudeste
            ("São Paulo", Estado.SP, "Rio de Janeiro", Estado.RJ, 430, 6.5, 45.80),
            ("São Paulo", Estado.SP, "Belo Horizonte", Estado.MG, 586, 8.5, 52.30),
            ("São Paulo", Estado.SP, "Curitiba", Estado.PR, 408, 6.0, 38.90),
            ("São Paulo", Estado.SP, "Campinas", Estado.SP, 96, 1.5, 12.50),
            ("São Paulo", Estado.SP, "Santos", Estado.SP, 72, 1.2, 18.70),
            ("Rio de Janeiro", Estado.RJ, "Belo Horizonte", Estado.MG, 434, 7.0, 41.20),
            ("Rio de Janeiro", Estado.RJ, "Vitória", Estado.ES, 521, 8.0, 48.60),
            ("Campinas", Estado.SP, "Belo Horizonte", Estado.MG, 494, 7.5, 44.30),
            # Sul
            ("Curitiba", Estado.PR, "Porto Alegre", Estado.RS, 711, 10.5, 62.40),
            ("Curitiba", Estado.PR, "Florianópolis", Estado.SC, 300, 4.5, 28.90),
            ("Porto Alegre", Estado.RS, "Florianópolis", Estado.SC, 476, 7.0, 38.50),
            ("Florianópolis", Estado.SC, "Joinville", Estado.SC, 180, 2.5, 15.30),
            # Centro-Oeste
            ("São Paulo", Estado.SP, "Brasília", Estado.DF, 1015, 14.0, 78.90),
            ("Brasília", Estado.DF, "Goiânia", Estado.GO, 209, 3.0, 18.40),
            ("Brasília", Estado.DF, "Belo Horizonte", Estado.MG, 741, 10.5, 64.20),
            ("Goiânia", Estado.GO, "Campo Grande", Estado.MS, 935, 13.0, 72.50),
            ("Campo Grande", Estado.MS, "Cuiabá", Estado.MT, 694, 10.0, 58.30),
            # Nordeste
            ("Salvador", Estado.BA, "Recife", Estado.PE, 839, 12.0, 68.70),
            ("Salvador", Estado.BA, "Fortaleza", Estado.CE, 1389, 19.0, 95.40),
            ("Recife", Estado.PE, "Fortaleza", Estado.CE, 800, 11.5, 65.80),
            ("Recife", Estado.PE, "Natal", Estado.RN, 297, 4.5, 24.60),
            ("Natal", Estado.RN, "João Pessoa", Estado.PB, 185, 2.8, 16.20),
            ("Recife", Estado.PE, "Maceió", Estado.AL, 285, 4.2, 23.50),
            ("Fortaleza", Estado.CE, "Natal", Estado.RN, 537, 7.8, 42.30),
            # Norte
            ("Brasília", Estado.DF, "Palmas", Estado.TO, 973, 13.5, 74.80),
            ("Palmas", Estado.TO, "Belém", Estado.PA, 1291, 18.0, 88.90),
            ("Belém", Estado.PA, "Manaus", Estado.AM, 1306, 18.5, 92.40),
            ("Porto Velho", Estado.RO, "Cuiabá", Estado.MT, 1456, 20.0, 98.60),
            # Conexões importantes
            ("Belo Horizonte", Estado.MG, "Salvador", Estado.BA, 1372, 19.0, 94.50),
            ("São Paulo", Estado.SP, "Salvador", Estado.BA, 1962, 27.0, 135.70),
        ]

        created_count = 0
        updated_count = 0
        error_count = 0

        for origem_nome, origem_estado, destino_nome, destino_estado, distancia, tempo, pedagio in rotas_data:
            try:
                cidade_origem = Cidade.objects.get(nome=origem_nome, estado=origem_estado)
                cidade_destino = Cidade.objects.get(nome=destino_nome, estado=destino_estado)

                rota, created = Rota.objects.update_or_create(
                    origem=cidade_origem,
                    destino=cidade_destino,
                    defaults={
                        "distancia_km": Decimal(str(distancia)),
                        "tempo_estimado_horas": Decimal(str(tempo)),
                        "pedagio_valor": Decimal(str(pedagio)),
                        "ativa": True,
                    },
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Criada: {rota.origem.nome_completo} → {rota.destino.nome_completo} ({distancia} km)"
                        )
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"→ Atualizada: {rota.origem.nome_completo} → {rota.destino.nome_completo} ({distancia} km)"
                        )
                    )

            except Cidade.DoesNotExist:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Erro: Cidade não encontrada para rota "
                        f"{origem_nome}/{origem_estado} → {destino_nome}/{destino_estado}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Processo concluído!\n"
                f"   Rotas criadas: {created_count}\n"
                f"   Rotas atualizadas: {updated_count}\n"
                f"   Erros: {error_count}\n"
                f"   Total: {created_count + updated_count}"
            )
        )

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING("\n⚠️  Execute 'python manage.py popular_cidades' antes de popular rotas.")
            )
