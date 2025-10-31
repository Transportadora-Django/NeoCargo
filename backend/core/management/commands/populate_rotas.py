"""
Comando para popular rotas e cidades iniciais.
Usado no deploy para garantir dados básicos no sistema.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.rotas.models import Cidade, ConfiguracaoPreco, Rota


class Command(BaseCommand):
    help = "Popula rotas e cidades iniciais no sistema"

    def handle(self, *args, **options):
        self.stdout.write("🌍 Populando cidades e rotas...")

        try:
            with transaction.atomic():
                # Verificar se já existem cidades
                cidade_count = Cidade.objects.count()
                self.stdout.write(f"📊 Cidades existentes: {cidade_count}")

                if cidade_count > 0:
                    self.stdout.write(self.style.WARNING(f"⚠️  {cidade_count} cidades já existem. Pulando população..."))
                    return

                # Criar cidades principais
                cidades_data = [
                    # São Paulo
                    {"nome": "São Paulo", "estado": "SP"},
                    {"nome": "Campinas", "estado": "SP"},
                    {"nome": "Santos", "estado": "SP"},
                    {"nome": "São José dos Campos", "estado": "SP"},
                    {"nome": "Ribeirão Preto", "estado": "SP"},
                    # Rio de Janeiro
                    {"nome": "Rio de Janeiro", "estado": "RJ"},
                    {"nome": "Niterói", "estado": "RJ"},
                    {"nome": "Campos dos Goytacazes", "estado": "RJ"},
                    # Minas Gerais
                    {"nome": "Belo Horizonte", "estado": "MG"},
                    {"nome": "Uberlândia", "estado": "MG"},
                    {"nome": "Juiz de Fora", "estado": "MG"},
                    # Espírito Santo
                    {"nome": "Vitória", "estado": "ES"},
                    {"nome": "Vila Velha", "estado": "ES"},
                    # Bahia
                    {"nome": "Salvador", "estado": "BA"},
                    {"nome": "Feira de Santana", "estado": "BA"},
                    # Paraná
                    {"nome": "Curitiba", "estado": "PR"},
                    {"nome": "Londrina", "estado": "PR"},
                    {"nome": "Maringá", "estado": "PR"},
                    # Santa Catarina
                    {"nome": "Florianópolis", "estado": "SC"},
                    {"nome": "Joinville", "estado": "SC"},
                    {"nome": "Blumenau", "estado": "SC"},
                    # Rio Grande do Sul
                    {"nome": "Porto Alegre", "estado": "RS"},
                    {"nome": "Caxias do Sul", "estado": "RS"},
                    # Distrito Federal
                    {"nome": "Brasília", "estado": "DF"},
                    # Goiás
                    {"nome": "Goiânia", "estado": "GO"},
                    # Pernambuco
                    {"nome": "Recife", "estado": "PE"},
                    # Ceará
                    {"nome": "Fortaleza", "estado": "CE"},
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
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Belo Horizonte-MG",
                        "distancia_km": 586,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Curitiba-PR",
                        "distancia_km": 408,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Brasília-DF",
                        "distancia_km": 1015,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Campinas-SP",
                        "distancia_km": 96,
                    },
                    {
                        "origem": "São Paulo-SP",
                        "destino": "Santos-SP",
                        "distancia_km": 72,
                    },
                    # Rotas RJ
                    {
                        "origem": "Rio de Janeiro-RJ",
                        "destino": "Belo Horizonte-MG",
                        "distancia_km": 434,
                    },
                    {
                        "origem": "Rio de Janeiro-RJ",
                        "destino": "Vitória-ES",
                        "distancia_km": 521,
                    },
                    {
                        "origem": "Rio de Janeiro-RJ",
                        "destino": "Salvador-BA",
                        "distancia_km": 1649,
                    },
                    # Rotas Sul
                    {
                        "origem": "Curitiba-PR",
                        "destino": "Florianópolis-SC",
                        "distancia_km": 300,
                    },
                    {
                        "origem": "Curitiba-PR",
                        "destino": "Porto Alegre-RS",
                        "distancia_km": 711,
                    },
                    {
                        "origem": "Florianópolis-SC",
                        "destino": "Porto Alegre-RS",
                        "distancia_km": 476,
                    },
                    # Rotas Nordeste
                    {
                        "origem": "Salvador-BA",
                        "destino": "Recife-PE",
                        "distancia_km": 839,
                    },
                    {
                        "origem": "Recife-PE",
                        "destino": "Fortaleza-CE",
                        "distancia_km": 800,
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
                        )
                        rotas_criadas += 1
                        self.stdout.write(
                            f"  ✓ Rota criada: {rota.origem.nome} → {rota.destino.nome} ({rota.distancia_km}km)"
                        )

                self.stdout.write(self.style.SUCCESS(f"✅ {rotas_criadas} rotas criadas com sucesso!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao popular rotas: {str(e)}"))
            raise
