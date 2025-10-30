"""
Comando para popular banco de dados com motoristas e veículos de teste.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from apps.contas.models import Profile, Role
from apps.motoristas.models import Motorista, CategoriaCNH
from apps.veiculos.models import Veiculo, EspecificacaoVeiculo
from apps.rotas.models import Cidade


class Command(BaseCommand):
    help = "Popula banco de dados com motoristas e veículos de teste"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove motoristas e veículos existentes antes de criar novos",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🚛 Populando banco com motoristas e veículos...\n")

        # Verifica se as cidades existem
        cidades = {
            "SP": Cidade.objects.filter(nome="São Paulo", estado="SP").first(),
            "RJ": Cidade.objects.filter(nome="Rio de Janeiro", estado="RJ").first(),
            "MG": Cidade.objects.filter(nome="Belo Horizonte", estado="MG").first(),
            "PR": Cidade.objects.filter(nome="Curitiba", estado="PR").first(),
            "RS": Cidade.objects.filter(nome="Porto Alegre", estado="RS").first(),
            "BA": Cidade.objects.filter(nome="Salvador", estado="BA").first(),
            "DF": Cidade.objects.filter(nome="Brasília", estado="DF").first(),
            "GO": Cidade.objects.filter(nome="Goiânia", estado="GO").first(),
        }

        missing_cities = [city for city, obj in cidades.items() if obj is None]
        if missing_cities:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Cidades não encontradas: {', '.join(missing_cities)}\n"
                    f"Execute: python manage.py popular_cidades"
                )
            )
            return

        # Verifica se as especificações de veículos existem
        specs = {}
        for tipo in ["carreta", "van", "carro", "moto"]:
            spec = EspecificacaoVeiculo.objects.filter(tipo=tipo).first()
            if not spec:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Especificação de veículo '{tipo}' não encontrada\n"
                        f"Execute: python manage.py popular_especificacoes"
                    )
                )
                return
            specs[tipo] = spec

        # Limpa dados existentes se solicitado
        if options["clear"]:
            self.stdout.write(self.style.WARNING("⚠️  Removendo dados existentes..."))
            Veiculo.objects.filter(placa__startswith="SEED").delete()
            Motorista.objects.filter(profile__user__username__startswith="motorista_").delete()
            User.objects.filter(username__startswith="motorista_").delete()
            self.stdout.write(self.style.SUCCESS("✓ Dados removidos\n"))

        # Dados dos motoristas
        motoristas_data = [
            {
                "username": "motorista_joao",
                "first_name": "João",
                "last_name": "Silva",
                "email": "joao.silva@neocargo.com",
                "cnh": CategoriaCNH.D,
                "sede": cidades["SP"],
                "entregas": 45,
            },
            {
                "username": "motorista_maria",
                "first_name": "Maria",
                "last_name": "Santos",
                "email": "maria.santos@neocargo.com",
                "cnh": CategoriaCNH.E,
                "sede": cidades["RJ"],
                "entregas": 78,
            },
            {
                "username": "motorista_pedro",
                "first_name": "Pedro",
                "last_name": "Costa",
                "email": "pedro.costa@neocargo.com",
                "cnh": CategoriaCNH.C,
                "sede": cidades["MG"],
                "entregas": 32,
            },
            {
                "username": "motorista_ana",
                "first_name": "Ana",
                "last_name": "Oliveira",
                "email": "ana.oliveira@neocargo.com",
                "cnh": CategoriaCNH.D,
                "sede": cidades["PR"],
                "entregas": 56,
            },
            {
                "username": "motorista_carlos",
                "first_name": "Carlos",
                "last_name": "Ferreira",
                "email": "carlos.ferreira@neocargo.com",
                "cnh": CategoriaCNH.E,
                "sede": cidades["RS"],
                "entregas": 91,
            },
            {
                "username": "motorista_lucia",
                "first_name": "Lúcia",
                "last_name": "Almeida",
                "email": "lucia.almeida@neocargo.com",
                "cnh": CategoriaCNH.B,
                "sede": cidades["BA"],
                "entregas": 12,
            },
            {
                "username": "motorista_roberto",
                "first_name": "Roberto",
                "last_name": "Mendes",
                "email": "roberto.mendes@neocargo.com",
                "cnh": CategoriaCNH.C,
                "sede": cidades["SP"],
                "entregas": 67,
            },
            {
                "username": "motorista_fernanda",
                "first_name": "Fernanda",
                "last_name": "Lima",
                "email": "fernanda.lima@neocargo.com",
                "cnh": CategoriaCNH.D,
                "sede": cidades["RJ"],
                "entregas": 43,
            },
            {
                "username": "motorista_ricardo",
                "first_name": "Ricardo",
                "last_name": "Souza",
                "email": "ricardo.souza@neocargo.com",
                "cnh": CategoriaCNH.D,
                "sede": cidades["DF"],
                "entregas": 28,
            },
            {
                "username": "motorista_juliana",
                "first_name": "Juliana",
                "last_name": "Martins",
                "email": "juliana.martins@neocargo.com",
                "cnh": CategoriaCNH.C,
                "sede": cidades["GO"],
                "entregas": 35,
            },
        ]

        # Dados dos veículos
        veiculos_data = [
            {
                "placa": "SEED-001",
                "marca": "Mercedes-Benz",
                "modelo": "Actros 2651",
                "ano": 2022,
                "cor": "Branco",
                "especificacao": specs["carreta"],
                "cnh_minima": CategoriaCNH.E,
                "sede": cidades["SP"],
            },
            {
                "placa": "SEED-002",
                "marca": "Volvo",
                "modelo": "FH 540",
                "ano": 2021,
                "cor": "Azul",
                "especificacao": specs["carreta"],
                "cnh_minima": CategoriaCNH.E,
                "sede": cidades["RJ"],
            },
            {
                "placa": "SEED-003",
                "marca": "Iveco",
                "modelo": "Daily 70C16",
                "ano": 2023,
                "cor": "Branco",
                "especificacao": specs["van"],
                "cnh_minima": CategoriaCNH.D,
                "sede": cidades["MG"],
            },
            {
                "placa": "SEED-004",
                "marca": "Volkswagen",
                "modelo": "Constellation 24.280",
                "ano": 2022,
                "cor": "Vermelho",
                "especificacao": specs["carreta"],
                "cnh_minima": CategoriaCNH.D,
                "sede": cidades["PR"],
            },
            {
                "placa": "SEED-005",
                "marca": "Renault",
                "modelo": "Master",
                "ano": 2023,
                "cor": "Prata",
                "especificacao": specs["van"],
                "cnh_minima": CategoriaCNH.C,
                "sede": cidades["RS"],
            },
            {
                "placa": "SEED-006",
                "marca": "Fiat",
                "modelo": "Ducato",
                "ano": 2022,
                "cor": "Branco",
                "especificacao": specs["van"],
                "cnh_minima": CategoriaCNH.C,
                "sede": cidades["BA"],
            },
            {
                "placa": "SEED-007",
                "marca": "Toyota",
                "modelo": "Hilux",
                "ano": 2023,
                "cor": "Preto",
                "especificacao": specs["carro"],
                "cnh_minima": CategoriaCNH.B,
                "sede": cidades["SP"],
            },
            {
                "placa": "SEED-008",
                "marca": "Ford",
                "modelo": "Cargo 1719",
                "ano": 2021,
                "cor": "Azul",
                "especificacao": specs["carreta"],
                "cnh_minima": CategoriaCNH.D,
                "sede": cidades["RJ"],
            },
            {
                "placa": "SEED-009",
                "marca": "Chevrolet",
                "modelo": "S10",
                "ano": 2023,
                "cor": "Branco",
                "especificacao": specs["carro"],
                "cnh_minima": CategoriaCNH.B,
                "sede": cidades["MG"],
            },
            {
                "placa": "SEED-010",
                "marca": "Honda",
                "modelo": "CG 160",
                "ano": 2023,
                "cor": "Vermelho",
                "especificacao": specs["moto"],
                "cnh_minima": CategoriaCNH.B,
                "sede": cidades["PR"],
            },
            {
                "placa": "SEED-011",
                "marca": "Mercedes-Benz",
                "modelo": "Sprinter",
                "ano": 2022,
                "cor": "Branco",
                "especificacao": specs["van"],
                "cnh_minima": CategoriaCNH.D,
                "sede": cidades["DF"],
            },
            {
                "placa": "SEED-012",
                "marca": "Iveco",
                "modelo": "Daily",
                "ano": 2023,
                "cor": "Prata",
                "especificacao": specs["van"],
                "cnh_minima": CategoriaCNH.C,
                "sede": cidades["GO"],
            },
        ]

        # Cria motoristas
        motoristas_criados = 0
        motoristas_existentes = 0

        for data in motoristas_data:
            user, user_created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                },
            )

            if user_created:
                user.set_password("senha123")  # Senha padrão para testes
                user.save()

            profile, profile_created = Profile.objects.get_or_create(user=user, defaults={"role": Role.MOTORISTA})

            if not profile_created and profile.role != Role.MOTORISTA:
                profile.role = Role.MOTORISTA
                profile.save()

            motorista, motorista_created = Motorista.objects.get_or_create(
                profile=profile,
                defaults={
                    "sede_atual": data["sede"],
                    "cnh_categoria": data["cnh"],
                    "entregas_concluidas": data["entregas"],
                    "disponivel": True,
                },
            )

            if motorista_created:
                motoristas_criados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Motorista criado: {user.get_full_name()} "
                        f"(CNH {data['cnh']}) - {data['sede'].nome_completo}"
                    )
                )
            else:
                motoristas_existentes += 1
                self.stdout.write(
                    self.style.WARNING(f"→ Motorista já existe: {user.get_full_name()} (CNH {data['cnh']})")
                )

        # Cria veículos
        veiculos_criados = 0
        veiculos_existentes = 0

        self.stdout.write("")  # Linha em branco

        for data in veiculos_data:
            veiculo, created = Veiculo.objects.get_or_create(
                placa=data["placa"],
                defaults={
                    "marca": data["marca"],
                    "modelo": data["modelo"],
                    "ano": data["ano"],
                    "cor": data["cor"],
                    "especificacao": data["especificacao"],
                    "categoria_minima_cnh": data["cnh_minima"],
                    "sede_atual": data["sede"],
                    "ativo": True,
                },
            )

            if created:
                veiculos_criados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Veículo criado: {data['marca']} {data['modelo']} "
                        f"({data['placa']}) - CNH {data['cnh_minima']} - {data['sede'].nome_completo}"
                    )
                )
            else:
                veiculos_existentes += 1
                self.stdout.write(
                    self.style.WARNING(f"→ Veículo já existe: {data['marca']} {data['modelo']} ({data['placa']})")
                )

        # Resumo
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Processo concluído!\n"
                f"   Motoristas criados: {motoristas_criados}\n"
                f"   Motoristas já existentes: {motoristas_existentes}\n"
                f"   Veículos criados: {veiculos_criados}\n"
                f"   Veículos já existentes: {veiculos_existentes}\n"
                f"   Total: {motoristas_criados + motoristas_existentes} motoristas, "
                f"{veiculos_criados + veiculos_existentes} veículos"
            )
        )

        # Dica de uso
        self.stdout.write(
            self.style.WARNING(
                "\n💡 Dica: Os motoristas foram criados com senha padrão 'senha123'\n"
                "   Use --clear para remover todos os dados de seed antes de recriar"
            )
        )
