from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sites.models import Site
from apps.contas.views import send_email_change_confirmation
from apps.contas.models import EmailChangeRequest


class Command(BaseCommand):
    help = "Testa o envio de email de notificação de mudança"

    def add_arguments(self, parser):
        parser.add_argument("--old-email", type=str, help="Email antigo")
        parser.add_argument("--new-email", type=str, help="Email novo")
        parser.add_argument("--user-name", type=str, help="Nome do usuário")

    def handle(self, *args, **options):
        # Configurar site padrão se não existir
        site, created = Site.objects.get_or_create(
            id=1, defaults={"domain": "localhost:8000", "name": "NeoCargo Local"}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Site criado: {site.name}"))

        # Criar uma requisição fake
        factory = RequestFactory()
        request = factory.post("/fake/", HTTP_HOST="localhost:8000")
        request.user = User(username="testuser")

        # Usar valores padrão ou fornecidos
        old_email = options["old_email"] or "antigo@example.com"
        new_email = options["new_email"] or "novo@example.com"
        user_name = options["user_name"] or "Usuário Teste"

        self.stdout.write("Testando envio de email...")
        self.stdout.write(f"Email antigo: {old_email}")
        self.stdout.write(f"Email novo: {new_email}")
        self.stdout.write(f"Nome: {user_name}")

        # Criar usuário de teste se não existir
        user, created = User.objects.get_or_create(
            username="test_user", defaults={"email": old_email, "first_name": user_name}
        )

        # Criar solicitação de mudança de email
        email_request = EmailChangeRequest.objects.create(user=user, old_email=old_email, new_email=new_email)

        # Testar o envio
        result = send_email_change_confirmation(email_change_request=email_request, request=request)

        if result:
            self.stdout.write(self.style.SUCCESS("✅ Email enviado com sucesso!"))
            self.stdout.write("🔗 Verifique o MailHog em: http://localhost:8025")
        else:
            self.stdout.write(self.style.ERROR("❌ Falha ao enviar email."))
