from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.contas.models import Profile, Role


class Command(BaseCommand):
    help = "Cria um usuário dono para testes"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, default="dono", help="Username do dono")
        parser.add_argument("--email", type=str, default="dono@neocargo.com", help="Email do dono")
        parser.add_argument("--password", type=str, default="dono123", help="Senha do dono")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        # Verifica se já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Usuário {username} já existe!"))
            return

        # Cria o usuário
        user = User.objects.create_user(
            username=username, email=email, password=password, first_name="Dono", last_name="NeoCargo"
        )

        # Cria ou atualiza o perfil como dono
        perfil, created = Profile.objects.get_or_create(user=user, defaults={"role": Role.OWNER})

        if not created:
            perfil.role = Role.OWNER
            perfil.save()

        self.stdout.write(self.style.SUCCESS("✅ Usuário dono criado com sucesso!"))
        self.stdout.write(f"Username: {username}")
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Senha: {password}")
        self.stdout.write(f"Role: {perfil.get_role_display()}")
