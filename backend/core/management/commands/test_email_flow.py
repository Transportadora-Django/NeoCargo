from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client
from apps.contas.models import EmailChangeRequest


class Command(BaseCommand):
    help = "Testa o fluxo completo de mudança de email"

    def handle(self, *args, **options):
        # Criar ou obter usuário de teste
        user, created = User.objects.get_or_create(
            username="test_email_flow",
            defaults={"email": "original@example.com", "first_name": "Test", "last_name": "User", "is_active": True},
        )

        if created:
            user.set_password("senha123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Usuário criado: {user.username}"))
        else:
            # Resetar email para o original
            user.email = "original@example.com"
            user.save()
            self.stdout.write(self.style.WARNING(f"⚠️ Usuário já existe: {user.username}"))

        # Limpar solicitações anteriores
        EmailChangeRequest.objects.filter(user=user).delete()

        # Simular login e mudança de email
        client = Client()
        client.force_login(user)

        self.stdout.write("")
        self.stdout.write("📋 Testando mudança de email...")
        self.stdout.write(f"   Email atual: {user.email}")

        # Tentar mudar email
        response = client.post(
            "/contas/perfil/",
            {"form_type": "user_data", "first_name": "Test", "last_name": "User", "email": "novo@example.com"},
        )

        # Verificar se redirecionou
        self.stdout.write(f"   Response status: {response.status_code}")

        # Verificar se o email NÃO foi alterado
        user.refresh_from_db()
        self.stdout.write(f"   Email após POST: {user.email}")

        # Verificar se foi criada solicitação
        requests = EmailChangeRequest.objects.filter(user=user, confirmed=False)
        self.stdout.write(f"   Solicitações pendentes: {requests.count()}")

        if requests.exists():
            request = requests.first()
            self.stdout.write(self.style.SUCCESS("✅ Solicitação criada!"))
            self.stdout.write(f"   Email antigo: {request.old_email}")
            self.stdout.write(f"   Email novo: {request.new_email}")
            self.stdout.write(f"   Token: {request.token}")
            self.stdout.write(f"   URL confirmação: /contas/confirmar-email/{request.token}/")
        else:
            self.stdout.write(self.style.ERROR("❌ Nenhuma solicitação foi criada!"))

        self.stdout.write("")
        self.stdout.write("🔗 Para testar:")
        self.stdout.write("   1. Login: http://localhost:8000/contas/login/")
        self.stdout.write(f"   2. Username: {user.username}")
        self.stdout.write("   3. Senha: senha123")
        self.stdout.write("   4. Vá em perfil e tente alterar email")
        self.stdout.write("   5. Verifique MailHog: http://localhost:8025")
