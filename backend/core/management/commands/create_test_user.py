from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.contas.models import Profile, Role


class Command(BaseCommand):
    help = "Cria um usuário de teste para validar o sistema de email"

    def handle(self, *args, **options):
        # Criar ou obter usuário de teste
        user, created = User.objects.get_or_create(
            username="usuario_teste",
            defaults={"email": "teste@example.com", "first_name": "Usuário", "last_name": "Teste", "is_active": True},
        )

        if created:
            user.set_password("senha123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Usuário criado: {user.username}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Usuário já existe: {user.username}"))

        # Criar ou obter perfil
        profile, profile_created = Profile.objects.get_or_create(user=user, defaults={"role": Role.CLIENTE})

        if profile_created:
            self.stdout.write(self.style.SUCCESS(f"✅ Perfil criado para {user.username}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Perfil já existe para {user.username}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("📋 Dados para teste:"))
        self.stdout.write(f"   Username: {user.username}")
        self.stdout.write(f"   Email: {user.email}")
        self.stdout.write("   Senha: senha123")
        self.stdout.write("")
        self.stdout.write("🔗 Acesse: http://localhost:8000/contas/login/")
        self.stdout.write("🔗 MailHog: http://localhost:8025/")
