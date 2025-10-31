"""
Comando para criar o primeiro superuser/owner automaticamente.
Usado no deploy para garantir que sempre exista um usuário admin.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.contas.models import Profile, Role


User = get_user_model()


class Command(BaseCommand):
    help = "Cria o primeiro superuser/owner automaticamente se não existir"

    def handle(self, *args, **options):
        # Verificar se já existe algum superuser
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING("⚠️  Superuser já existe. Pulando criação...")
            )
            return

        # Obter credenciais das variáveis de ambiente
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "neocargo.testes@gmail.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "❌ DJANGO_SUPERUSER_PASSWORD não definido. "
                    "Defina a variável de ambiente para criar o superuser."
                )
            )
            return

        try:
            # Criar superuser
            user = User.objects.create_superuser(
                username=username, email=email, password=password
            )

            # Garantir que o profile seja criado com role OWNER
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = Role.OWNER
            profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Superuser criado com sucesso!\n"
                    f"   Username: {username}\n"
                    f"   Email: {email}\n"
                    f"   Role: Owner"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao criar superuser: {str(e)}")
            )
