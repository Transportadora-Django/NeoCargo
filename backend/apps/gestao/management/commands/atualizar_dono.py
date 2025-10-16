from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.contas.models import Profile, Role


class Command(BaseCommand):
    help = "Atualiza um usuário existente para o role de Owner/Dono"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username do usuário a ser promovido a dono")

    def handle(self, *args, **options):
        username = options["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuário "{username}" não encontrado!'))
            return

        # Cria ou atualiza o perfil
        profile, created = Profile.objects.get_or_create(user=user)

        old_role = profile.get_role_display()
        profile.role = Role.OWNER
        profile.save()

        self.stdout.write(self.style.SUCCESS(f'✅ Usuário "{username}" atualizado com sucesso!'))
        self.stdout.write(f"   Role anterior: {old_role}")
        self.stdout.write(f"   Novo role: {profile.get_role_display()}")
        self.stdout.write(f"   Email: {user.email}")
        self.stdout.write(f"   Nome: {user.get_full_name() or user.username}")
