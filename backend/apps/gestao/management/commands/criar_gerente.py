"""
Comando para criar um usuário gerente de teste
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.contas.models import Profile, Role


class Command(BaseCommand):
    help = "Cria um usuário gerente para testes"

    def handle(self, *args, **kwargs):
        username = "gerente"
        email = "gerente@neocargo.com"
        password = "gerente123"

        # Verifica se já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Usuário '{username}' já existe!"))
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)

            # Atualiza o role se necessário
            if profile.role != Role.GERENTE:
                profile.role = Role.GERENTE
                profile.save()
                self.stdout.write(self.style.SUCCESS(f"Role do usuário '{username}' atualizado para GERENTE"))
        else:
            # Cria o usuário
            user = User.objects.create_user(
                username=username, email=email, password=password, first_name="Gerente", last_name="Teste"
            )

            # Atualiza o profile
            profile = Profile.objects.get(user=user)
            profile.role = Role.GERENTE
            profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Gerente criado com sucesso!\n"
                    f"   Username: {username}\n"
                    f"   Email: {email}\n"
                    f"   Senha: {password}\n"
                )
            )

        return f"Gerente: {username}"
