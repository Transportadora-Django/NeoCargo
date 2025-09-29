from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.contas.models import EmailChangeRequest
from apps.contas.forms import UserEditForm


class Command(BaseCommand):
    help = "Debug de mudança de email"

    def handle(self, *args, **options):
        # Encontrar usuário com email user2@tester.com
        try:
            user = User.objects.get(email="user2@tester.com")
        except User.DoesNotExist:
            # Tentar encontrar qualquer usuário
            users = User.objects.all()
            self.stdout.write("Usuários encontrados:")
            for u in users:
                self.stdout.write(f"  - {u.username}: {u.email}")
            return

        self.stdout.write("✅ Usuário encontrado:")
        self.stdout.write(f"   Username: {user.username}")
        self.stdout.write(f"   Email: {user.email}")
        self.stdout.write(f"   First name: {user.first_name}")
        self.stdout.write(f"   Last name: {user.last_name}")

        # Testar formulário
        self.stdout.write("\n📝 Testando formulário:")

        # Simular dados do formulário
        form_data = {"full_name": "User Tester", "email": "novo@example.com"}

        form = UserEditForm(data=form_data, instance=user)

        self.stdout.write(f"   Formulário válido: {form.is_valid()}")

        if not form.is_valid():
            self.stdout.write(f"   Erros: {form.errors}")

        # Testar a comparação de emails
        old_email = user.email
        new_email = form_data["email"]
        email_changed = old_email != new_email

        self.stdout.write(f'   Email antigo: "{old_email}"')
        self.stdout.write(f'   Email novo: "{new_email}"')
        self.stdout.write(f"   Tipos: {type(old_email)} vs {type(new_email)}")
        self.stdout.write(f"   Email mudou: {email_changed}")

        # Verificar solicitações pendentes
        pending_requests = EmailChangeRequest.objects.filter(user=user, confirmed=False).count()

        self.stdout.write(f"\n📧 Solicitações pendentes: {pending_requests}")
