"""
Comando para popular rotas e cidades iniciais.
Usado no deploy para garantir dados básicos no sistema.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.rotas.models import Cidade, ConfiguracaoPreco, Rota


class Command(BaseCommand):
    help = "Popula rotas e cidades iniciais no sistema"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Força a atualização de coordenadas mesmo se cidades já existirem",
        )

    def handle(self, *args, **options):
        self.stdout.write("🌍 Populando cidades e rotas...")
        force = options.get("force", False)

        try:
            with transaction.atomic():
                # Verificar se já existem cidades
                cidade_count = Cidade.objects.count()
                self.stdout.write(f"📊 Cidades existentes: {cidade_count}")

                if cidade_count > 0 and not force:
                    self.stdout.write(self.style.WARNING(f"⚠️  {cidade_count} cidades já existem. Pulando população..."))
                    self.stdout.write(
                        self.style.WARNING("💡 Use --force para atualizar coordenadas das cidades existentes")
                    )
                    return

                # Se force=True, atualizar cidades existentes
                if cidade_count > 0 and force:
                    self.stdout.write(
                        self.style.WARNING(f"🔄 Modo --force: Atualizando {cidade_count} cidades existentes...")
                    )
                    return self._atualizar_cidades_existentes()

                # Criar cidades principais com coordenadas
                cidades_data = [
                    # São Paulo
                    {"nome": "São Paulo", "estado": "SP", "latitude": "-23.5505199", "longitude": "-46.6333094"},
                    {"nome": "Campinas", "estado": "SP", "latitude": "-22.9099384", "longitude": "-47.0626332"},
                    {"nome": "Santos", "estado": "SP", "latitude": "-23.9608647", "longitude": "-46.3334537"},
                    {
                        "nome": "São José dos Campos",
                        "estado": "SP",
                        "latitude": "-23.1790943",
                        "longitude": "-45.8869436",
                    },
                    {"nome": "Ribeirão Preto", "estado": "SP", "latitude": "-21.1704844", "longitude": "-47.8102816"},
                    # Rio de Janeiro
                    {"nome": "Rio de Janeiro", "estado": "RJ", "latitude": "-22.9068467", "longitude": "-43.1728965"},
                    {"nome": "Niterói", "estado": "RJ", "latitude": "-22.8838181", "longitude": "-43.1030647"},
                    {
                        "nome": "Campos dos Goytacazes",
                        "estado": "RJ",
                        "latitude": "-21.7621661",
                        "longitude": "-41.3194584",
                    },
                    # Minas Gerais
                    {"nome": "Belo Horizonte", "estado": "MG", "latitude": "-19.9166813", "longitude": "-43.9344931"},
                    {"nome": "Uberlândia", "estado": "MG", "latitude": "-18.9188149", "longitude": "-48.2766837"},
                    {"nome": "Juiz de Fora", "estado": "MG", "latitude": "-21.7641783", "longitude": "-43.3509286"},
                    # Espírito Santo
                    {"nome": "Vitória", "estado": "ES", "latitude": "-20.3155151", "longitude": "-40.3128767"},
                    {"nome": "Vila Velha", "estado": "ES", "latitude": "-20.3298826", "longitude": "-40.2925124"},
                    # Bahia
                    {"nome": "Salvador", "estado": "BA", "latitude": "-12.9714", "longitude": "-38.5014"},
                    {"nome": "Feira de Santana", "estado": "BA", "latitude": "-12.2664", "longitude": "-38.9663"},
                    # Paraná
                    {"nome": "Curitiba", "estado": "PR", "latitude": "-25.4284", "longitude": "-49.2733"},
                    {"nome": "Londrina", "estado": "PR", "latitude": "-23.3045", "longitude": "-51.1696"},
                    {"nome": "Maringá", "estado": "PR", "latitude": "-23.4209", "longitude": "-51.9333"},
                    # Santa Catarina
                    {"nome": "Florianópolis", "estado": "SC", "latitude": "-27.5954", "longitude": "-48.5480"},
                    {"nome": "Joinville", "estado": "SC", "latitude": "-26.3045", "longitude": "-48.8487"},
                    {"nome": "Blumenau", "estado": "SC", "latitude": "-26.9194", "longitude": "-49.0661"},
                    # Rio Grande do Sul
                    {"nome": "Porto Alegre", "estado": "RS", "latitude": "-30.0346", "longitude": "-51.2177"},
                    {"nome": "Caxias do Sul", "estado": "RS", "latitude": "-29.1634", "longitude": "-51.1797"},
                    # Distrito Federal
                    {"nome": "Brasília", "estado": "DF", "latitude": "-15.8267", "longitude": "-47.9218"},
                    # Goiás
                    {"nome": "Goiânia", "estado": "GO", "latitude": "-16.6869", "longitude": "-49.2648"},
                    # Pernambuco
                    {"nome": "Recife", "estado": "PE", "latitude": "-8.0476", "longitude": "-34.8770"},
                    # Ceará
                    {"nome": "Fortaleza", "estado": "CE", "latitude": "-3.7319", "longitude": "-38.5267"},
                ]

                cidades = {}
                for cidade_data in cidades_data:
                    cidade = Cidade.objects.create(**cidade_data)
                    cidades[f"{cidade.nome}-{cidade.estado}"] = cidade
                    self.stdout.write(f"  ✓ Cidade criada: {cidade}")

                self.stdout.write(self.style.SUCCESS(f"✅ {len(cidades)} cidades criadas com sucesso!"))

                # Criar configuração de preço padrão (se não existir)
                if not ConfiguracaoPreco.objects.exists():
                    ConfiguracaoPreco.objects.create()
                    self.stdout.write(self.style.SUCCESS("✅ Configuração de preço criada com valores padrão"))
                else:
                    self.stdout.write(self.style.WARNING("⚠️  Configuração de preço já existe"))

                # Criar rotas principais
                rotas_data = [
                    # Rotas SP
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Rio de Janeiro-RJ",
                        "distancia_km": 430,
                        "tempo_estimado_horas": 6.5,
                        "pedagio_valor": 45.80,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Belo Horizonte-MG",
                        "distancia_km": 586,
                        "tempo_estimado_horas": 8.5,
                        "pedagio_valor": 52.30,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Curitiba-PR",
                        "distancia_km": 408,
                        "tempo_estimado_horas": 6.0,
                        "pedagio_valor": 38.90,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Brasília-DF",
                        "distancia_km": 1015,
                        "tempo_estimado_horas": 14.0,
                        "pedagio_valor": 78.90,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Campinas-SP",
                        "distancia_km": 96,
                        "tempo_estimado_horas": 1.5,
                        "pedagio_valor": 12.50,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Santos-SP",
                        "distancia_km": 72,
                        "tempo_estimado_horas": 1.2,
                        "pedagio_valor": 18.70,
                    },
                    # Rotas RJ
                    {
                        "origem": "Rio de Janeiro-RJ",
                        "destino": "Belo Horizonte-MG",
                        "distancia_km": 434,
                        "tempo_estimado_horas": 7.0,
                        "pedagio_valor": 41.20,
                    },
                    {
                        "origem": "Rio de Janeiro-RJ",
                        "destino": "Vitória-ES",
                        "distancia_km": 521,
                        "tempo_estimado_horas": 8.0,
                        "pedagio_valor": 48.60,
                    },
                    {
                        "origem": "Rio de Janeiro-RJ",
                        "destino": "Salvador-BA",
                        "distancia_km": 1649,
                        "tempo_estimado_horas": 23.0,
                        "pedagio_valor": 112.30,
                    },
                    # Rotas Sul
                    {
                        "origem": "Curitiba-PR",
                        "destino": "Florianópolis-SC",
                        "distancia_km": 300,
                        "tempo_estimado_horas": 4.5,
                        "pedagio_valor": 28.90,
                    },
                    {
                        "origem": "Curitiba-PR",
                        "destino": "Porto Alegre-RS",
                        "distancia_km": 711,
                        "tempo_estimado_horas": 10.5,
                        "pedagio_valor": 62.40,
                    },
                    {
                        "origem": "Florianópolis-SC",
                        "destino": "Porto Alegre-RS",
                        "distancia_km": 476,
                        "tempo_estimado_horas": 7.0,
                        "pedagio_valor": 38.50,
                    },
                    # Rotas Nordeste
                    {
                        "origem": "Salvador-BA",
                        "destino": "Recife-PE",
                        "distancia_km": 839,
                        "tempo_estimado_horas": 12.0,
                        "pedagio_valor": 68.70,
                    },
                    {
                        "origem": "Recife-PE",
                        "destino": "Fortaleza-CE",
                        "distancia_km": 800,
                        "tempo_estimado_horas": 11.5,
                        "pedagio_valor": 65.80,
                    },
                    # Novas rotas para conectar todas as cidades
                    # Nordeste - conexões adicionais
                    {
                        "origem": "Salvador-BA",
                        "destino": "Fortaleza-CE",
                        "distancia_km": 1389,
                        "tempo_estimado_horas": 19.0,
                        "pedagio_valor": 95.40,
                    },
                    {
                        "origem": "Recife-PE",
                        "destino": "Natal-RN",
                        "distancia_km": 297,
                        "tempo_estimado_horas": 4.5,
                        "pedagio_valor": 24.60,
                    },
                    {
                        "origem": "Natal-RN",
                        "destino": "João Pessoa-PB",
                        "distancia_km": 185,
                        "tempo_estimado_horas": 2.8,
                        "pedagio_valor": 16.20,
                    },
                    {
                        "origem": "Natal-RN",
                        "destino": "Fortaleza-CE",
                        "distancia_km": 537,
                        "tempo_estimado_horas": 7.8,
                        "pedagio_valor": 42.30,
                    },
                    {
                        "origem": "Recife-PE",
                        "destino": "Maceió-AL",
                        "distancia_km": 285,
                        "tempo_estimado_horas": 4.2,
                        "pedagio_valor": 23.50,
                    },
                    {
                        "origem": "Recife-PE",
                        "destino": "João Pessoa-PB",
                        "distancia_km": 120,
                        "tempo_estimado_horas": 2.0,
                        "pedagio_valor": 12.80,
                    },
                    {
                        "origem": "Salvador-BA",
                        "destino": "Maceió-AL",
                        "distancia_km": 612,
                        "tempo_estimado_horas": 9.0,
                        "pedagio_valor": 48.90,
                    },
                    # Sul - conexões adicionais
                    {
                        "origem": "Florianópolis-SC",
                        "destino": "Joinville-SC",
                        "distancia_km": 180,
                        "tempo_estimado_horas": 2.5,
                        "pedagio_valor": 15.30,
                    },
                    {
                        "origem": "Curitiba-PR",
                        "destino": "Joinville-SC",
                        "distancia_km": 130,
                        "tempo_estimado_horas": 2.0,
                        "pedagio_valor": 14.20,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Florianópolis-SC",
                        "distancia_km": 705,
                        "tempo_estimado_horas": 10.0,
                        "pedagio_valor": 58.40,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Porto Alegre-RS",
                        "distancia_km": 1120,
                        "tempo_estimado_horas": 16.0,
                        "pedagio_valor": 85.30,
                    },
                    # Centro-Oeste - conectando as cidades isoladas
                    {
                        "origem": "Brasília-DF",
                        "destino": "Goiânia-GO",
                        "distancia_km": 209,
                        "tempo_estimado_horas": 3.0,
                        "pedagio_valor": 18.40,
                    },
                    {
                        "origem": "Brasília-DF",
                        "destino": "Belo Horizonte-MG",
                        "distancia_km": 741,
                        "tempo_estimado_horas": 10.5,
                        "pedagio_valor": 64.20,
                    },
                    {
                        "origem": "Brasília-DF",
                        "destino": "Palmas-TO",
                        "distancia_km": 973,
                        "tempo_estimado_horas": 13.5,
                        "pedagio_valor": 74.80,
                    },
                    {
                        "origem": "Goiânia-GO",
                        "destino": "Campo Grande-MS",
                        "distancia_km": 935,
                        "tempo_estimado_horas": 13.0,
                        "pedagio_valor": 72.50,
                    },
                    {
                        "origem": "Campo Grande-MS",
                        "destino": "Cuiabá-MT",
                        "distancia_km": 694,
                        "tempo_estimado_horas": 10.0,
                        "pedagio_valor": 58.30,
                    },
                    {
                        "origem": "Brasília-DF",
                        "destino": "Cuiabá-MT",
                        "distancia_km": 1133,
                        "tempo_estimado_horas": 15.5,
                        "pedagio_valor": 82.70,
                    },
                    # Norte - conectando Amazônia
                    {
                        "origem": "Palmas-TO",
                        "destino": "Belém-PA",
                        "distancia_km": 1291,
                        "tempo_estimado_horas": 18.0,
                        "pedagio_valor": 88.90,
                    },
                    {
                        "origem": "Belém-PA",
                        "destino": "Manaus-AM",
                        "distancia_km": 1306,
                        "tempo_estimado_horas": 18.5,
                        "pedagio_valor": 92.40,
                    },
                    {
                        "origem": "Porto Velho-RO",
                        "destino": "Cuiabá-MT",
                        "distancia_km": 1456,
                        "tempo_estimado_horas": 20.0,
                        "pedagio_valor": 98.60,
                    },
                    {
                        "origem": "Manaus-AM",
                        "destino": "Porto Velho-RO",
                        "distancia_km": 901,
                        "tempo_estimado_horas": 13.0,
                        "pedagio_valor": 68.50,
                    },
                    {
                        "origem": "Brasília-DF",
                        "destino": "Salvador-BA",
                        "distancia_km": 1446,
                        "tempo_estimado_horas": 20.0,
                        "pedagio_valor": 98.40,
                    },
                    # Conexões Sudeste
                    {
                        "origem": "Campinas-SP",
                        "destino": "Belo Horizonte-MG",
                        "distancia_km": 494,
                        "tempo_estimado_horas": 7.5,
                        "pedagio_valor": 44.30,
                    },
                    {
                        "origem": "Belo Horizonte-MG",
                        "destino": "Vitória-ES",
                        "distancia_km": 524,
                        "tempo_estimado_horas": 8.0,
                        "pedagio_valor": 46.80,
                    },
                    {
                        "origem": "Belo Horizonte-MG",
                        "destino": "Salvador-BA",
                        "distancia_km": 1372,
                        "tempo_estimado_horas": 19.0,
                        "pedagio_valor": 94.50,
                    },
                ]

                rotas_criadas = 0
                for rota_data in rotas_data:
                    origem_key = rota_data["origem"]
                    destino_key = rota_data["destino"]

                    if origem_key in cidades and destino_key in cidades:
                        rota = Rota.objects.create(
                            origem=cidades[origem_key],
                            destino=cidades[destino_key],
                            distancia_km=rota_data["distancia_km"],
                            tempo_estimado_horas=rota_data.get("tempo_estimado_horas"),
                            pedagio_valor=rota_data.get("pedagio_valor", 0),
                        )
                        rotas_criadas += 1
                        self.stdout.write(
                            f"  ✓ Rota criada: {rota.origem.nome} → {rota.destino.nome} ({rota.distancia_km}km)"
                        )

                self.stdout.write(self.style.SUCCESS(f"✅ {rotas_criadas} rotas criadas com sucesso!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao popular rotas: {str(e)}"))
            raise

    def _atualizar_cidades_existentes(self):
        """Atualiza coordenadas de cidades existentes."""
        # Mapa de coordenadas
        coordenadas_map = {
            ("São Paulo", "SP"): (Decimal("-23.5505199"), Decimal("-46.6333094")),
            ("Campinas", "SP"): (Decimal("-22.9099384"), Decimal("-47.0626332")),
            ("Santos", "SP"): (Decimal("-23.9608647"), Decimal("-46.3334537")),
            ("São José dos Campos", "SP"): (Decimal("-23.1790943"), Decimal("-45.8869436")),
            ("Ribeirão Preto", "SP"): (Decimal("-21.1704844"), Decimal("-47.8102816")),
            ("Rio de Janeiro", "RJ"): (Decimal("-22.9068467"), Decimal("-43.1728965")),
            ("Niterói", "RJ"): (Decimal("-22.8838181"), Decimal("-43.1030647")),
            ("Campos dos Goytacazes", "RJ"): (Decimal("-21.7621661"), Decimal("-41.3194584")),
            ("Belo Horizonte", "MG"): (Decimal("-19.9166813"), Decimal("-43.9344931")),
            ("Uberlândia", "MG"): (Decimal("-18.9188149"), Decimal("-48.2766837")),
            ("Juiz de Fora", "MG"): (Decimal("-21.7641783"), Decimal("-43.3509286")),
            ("Vitória", "ES"): (Decimal("-20.3155151"), Decimal("-40.3128767")),
            ("Vila Velha", "ES"): (Decimal("-20.3298826"), Decimal("-40.2925124")),
            ("Salvador", "BA"): (Decimal("-12.9714"), Decimal("-38.5014")),
            ("Feira de Santana", "BA"): (Decimal("-12.2664"), Decimal("-38.9663")),
            ("Curitiba", "PR"): (Decimal("-25.4284"), Decimal("-49.2733")),
            ("Londrina", "PR"): (Decimal("-23.3045"), Decimal("-51.1696")),
            ("Maringá", "PR"): (Decimal("-23.4209"), Decimal("-51.9333")),
            ("Florianópolis", "SC"): (Decimal("-27.5954"), Decimal("-48.5480")),
            ("Joinville", "SC"): (Decimal("-26.3045"), Decimal("-48.8487")),
            ("Blumenau", "SC"): (Decimal("-26.9194"), Decimal("-49.0661")),
            ("Porto Alegre", "RS"): (Decimal("-30.0346"), Decimal("-51.2177")),
            ("Caxias do Sul", "RS"): (Decimal("-29.1634"), Decimal("-51.1797")),
            ("Brasília", "DF"): (Decimal("-15.8267"), Decimal("-47.9218")),
            ("Goiânia", "GO"): (Decimal("-16.6869"), Decimal("-49.2648")),
            ("Recife", "PE"): (Decimal("-8.0476"), Decimal("-34.8770")),
            ("Fortaleza", "CE"): (Decimal("-3.7319"), Decimal("-38.5267")),
        }

        atualizadas = 0
        for (nome, estado), (lat, lng) in coordenadas_map.items():
            try:
                cidade = Cidade.objects.get(nome=nome, estado=estado)
                cidade.latitude = lat
                cidade.longitude = lng
                cidade.save()
                atualizadas += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Atualizada: {cidade.nome_completo}"))
            except Cidade.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠️  Não encontrada: {nome}/{estado}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ {atualizadas} cidades atualizadas com coordenadas!"))

        # Atualizar rotas existentes com tempo estimado e pedágio
        self.stdout.write("\n🛣️  Atualizando rotas existentes...")
        rotas_map = {
            # Rotas existentes
            ("Salvador", "BA", "Recife", "PE"): {"tempo": 12.0, "pedagio": 68.70},
            ("Recife", "PE", "Fortaleza", "CE"): {"tempo": 11.5, "pedagio": 65.80},
            ("Curitiba", "PR", "Florianópolis", "SC"): {"tempo": 4.5, "pedagio": 28.90},
            ("Curitiba", "PR", "Porto Alegre", "RS"): {"tempo": 10.5, "pedagio": 62.40},
            ("Rio de Janeiro", "RJ", "Vitória", "ES"): {"tempo": 8.0, "pedagio": 48.60},
            ("Rio de Janeiro", "RJ", "Belo Horizonte", "MG"): {"tempo": 7.0, "pedagio": 41.20},
            ("Rio de Janeiro", "RJ", "Salvador", "BA"): {"tempo": 23.0, "pedagio": 112.30},
            ("Florianópolis", "SC", "Porto Alegre", "RS"): {"tempo": 7.0, "pedagio": 38.50},
            ("São Paulo", "SP", "Belo Horizonte", "MG"): {"tempo": 8.5, "pedagio": 52.30},
            ("São Paulo", "SP", "Campinas", "SP"): {"tempo": 1.5, "pedagio": 12.50},
            ("São Paulo", "SP", "Rio de Janeiro", "RJ"): {"tempo": 6.5, "pedagio": 45.80},
            ("São Paulo", "SP", "Santos", "SP"): {"tempo": 1.2, "pedagio": 18.70},
            ("São Paulo", "SP", "Curitiba", "PR"): {"tempo": 6.0, "pedagio": 38.90},
            ("São Paulo", "SP", "Brasília", "DF"): {"tempo": 14.0, "pedagio": 78.90},
            # Novas rotas adicionadas
            ("Salvador", "BA", "Fortaleza", "CE"): {"tempo": 19.0, "pedagio": 95.40},
            ("Recife", "PE", "Natal", "RN"): {"tempo": 4.5, "pedagio": 24.60},
            ("Natal", "RN", "João Pessoa", "PB"): {"tempo": 2.8, "pedagio": 16.20},
            ("Natal", "RN", "Fortaleza", "CE"): {"tempo": 7.8, "pedagio": 42.30},
            ("Recife", "PE", "Maceió", "AL"): {"tempo": 4.2, "pedagio": 23.50},
            ("Recife", "PE", "João Pessoa", "PB"): {"tempo": 2.0, "pedagio": 12.80},
            ("Salvador", "BA", "Maceió", "AL"): {"tempo": 9.0, "pedagio": 48.90},
            ("Florianópolis", "SC", "Joinville", "SC"): {"tempo": 2.5, "pedagio": 15.30},
            ("Curitiba", "PR", "Joinville", "SC"): {"tempo": 2.0, "pedagio": 14.20},
            ("São Paulo", "SP", "Florianópolis", "SC"): {"tempo": 10.0, "pedagio": 58.40},
            ("São Paulo", "SP", "Porto Alegre", "RS"): {"tempo": 16.0, "pedagio": 85.30},
            ("Brasília", "DF", "Goiânia", "GO"): {"tempo": 3.0, "pedagio": 18.40},
            ("Brasília", "DF", "Belo Horizonte", "MG"): {"tempo": 10.5, "pedagio": 64.20},
            ("Brasília", "DF", "Palmas", "TO"): {"tempo": 13.5, "pedagio": 74.80},
            ("Goiânia", "GO", "Campo Grande", "MS"): {"tempo": 13.0, "pedagio": 72.50},
            ("Campo Grande", "MS", "Cuiabá", "MT"): {"tempo": 10.0, "pedagio": 58.30},
            ("Brasília", "DF", "Cuiabá", "MT"): {"tempo": 15.5, "pedagio": 82.70},
            ("Palmas", "TO", "Belém", "PA"): {"tempo": 18.0, "pedagio": 88.90},
            ("Belém", "PA", "Manaus", "AM"): {"tempo": 18.5, "pedagio": 92.40},
            ("Porto Velho", "RO", "Cuiabá", "MT"): {"tempo": 20.0, "pedagio": 98.60},
            ("Manaus", "AM", "Porto Velho", "RO"): {"tempo": 13.0, "pedagio": 68.50},
            ("Brasília", "DF", "Salvador", "BA"): {"tempo": 20.0, "pedagio": 98.40},
            ("Campinas", "SP", "Belo Horizonte", "MG"): {"tempo": 7.5, "pedagio": 44.30},
            ("Belo Horizonte", "MG", "Vitória", "ES"): {"tempo": 8.0, "pedagio": 46.80},
            ("Belo Horizonte", "MG", "Salvador", "BA"): {"tempo": 19.0, "pedagio": 94.50},
        }

        rotas_atualizadas = 0
        for rota_key, dados in rotas_map.items():
            origem_nome, origem_estado, destino_nome, destino_estado = rota_key
            try:
                origem = Cidade.objects.get(nome=origem_nome, estado=origem_estado)
                destino = Cidade.objects.get(nome=destino_nome, estado=destino_estado)

                rota = Rota.objects.filter(origem=origem, destino=destino).first()
                if rota:
                    rota.tempo_estimado_horas = Decimal(str(dados["tempo"]))
                    rota.pedagio_valor = Decimal(str(dados["pedagio"]))
                    rota.save()
                    rotas_atualizadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Rota atualizada: {rota.origem.nome} → {rota.destino.nome} "
                            f"({dados['tempo']}h, R${dados['pedagio']})"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Rota não encontrada: {origem_nome}/{origem_estado} → {destino_nome}/{destino_estado}"
                        )
                    )
            except Cidade.DoesNotExist as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Cidade não encontrada para rota "
                        f"{origem_nome}/{origem_estado} → {destino_nome}/{destino_estado}: {e}"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"\n✅ {rotas_atualizadas} rotas atualizadas!"))
