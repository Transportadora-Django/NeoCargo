from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from apps.contas.models import EmailChangeRequest


class Command(BaseCommand):
    help = "Simula o clique no botão salvar alterações"

    def handle(self, *args, **options):
        # Usar o usuário usuario_teste que existe e tem email limpo
        try:
            user = User.objects.get(username="usuario_teste")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Usuário usuario_teste não encontrado"))
            return

        client = Client()
        client.force_login(user)

        # Limpar solicitações anteriores
        EmailChangeRequest.objects.filter(user=user).delete()

        self.stdout.write(f"🧪 Testando com usuário: {user.username}")
        self.stdout.write(f"📧 Email atual: {user.email}")

        # Simular o POST que acontece quando você clica em "Salvar Alterações"
        # com um email diferente e único
        import uuid

        novo_email = f"teste_{uuid.uuid4().hex[:8]}@example.com"

        self.stdout.write(f"🎯 Tentando alterar para: {novo_email}")

        response = client.post(
            "/contas/perfil/",
            {
                "form_type": "user_data",
                "full_name": "User Tester",  # Nome atual
                "email": novo_email,  # Email novo
            },
            follow=True,
            HTTP_HOST="localhost:8000",
        )

        # Verificar o resultado
        self.stdout.write(f"📊 Status da resposta: {response.status_code}")

        # Verificar mensagens
        if response.context and "messages" in response.context:
            messages = list(response.context["messages"])
            if messages:
                for message in messages:
                    self.stdout.write(f"💬 Mensagem: {message}")
            else:
                self.stdout.write("💬 Nenhuma mensagem encontrada")
        else:
            self.stdout.write("💬 Context não disponível")

        # Verificar se o email foi alterado
        user.refresh_from_db()
        self.stdout.write(f"📧 Email após POST: {user.email}")

        # Verificar solicitações criadas
        requests = EmailChangeRequest.objects.filter(user=user, confirmed=False)
        self.stdout.write(f"📝 Solicitações criadas: {requests.count()}")

        for req in requests:
            self.stdout.write(f"   {req.old_email} -> {req.new_email}")

        self.stdout.write("✅ Teste concluído!")
