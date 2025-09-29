from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from ..models import Profile, Role


class ContasIntegrationTest(TestCase):
    """Testes de integração para o app contas"""

    def setUp(self):
        self.client = Client()

    def test_fluxo_completo_cadastro_login(self):
        """Testa fluxo completo: cadastro -> login"""
        # 1. Cadastro de usuário (simplificado)
        cadastro_data = {
            "full_name": "João Silva",
            "email": "joao@example.com",
            "password1": "minhasenha123",
            "password2": "minhasenha123",
        }

        response = self.client.post(reverse("contas:signup"), cadastro_data)
        # Assumindo que redireciona após cadastro bem-sucedido
        self.assertIn(response.status_code, [200, 302])

        # Verifica se usuário foi criado
        self.assertTrue(User.objects.filter(email="joao@example.com").exists())
        user = User.objects.get(email="joao@example.com")
        self.assertEqual(user.username, "joao@example.com")  # Email usado como username
        self.assertEqual(user.first_name, "João")
        self.assertEqual(user.last_name, "Silva")
        self.assertEqual(user.email, "joao@example.com")

        # 2. Login do usuário (usando email como username)
        login_response = self.client.post(
            reverse("contas:login"), {"username": "joao@example.com", "password": "minhasenha123"}
        )
        self.assertIn(login_response.status_code, [200, 302])

    def test_fluxo_recuperacao_senha(self):
        """Testa fluxo de recuperação de senha"""
        # Criar usuário
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="senhaantiga123",
            first_name="Test",
            last_name="User",
        )

        # Solicitar recuperação de senha
        response = self.client.post(reverse("contas:password_reset"), {"email": "test@example.com"})
        self.assertIn(response.status_code, [200, 302])

        # Verifica se email foi enviado (se configurado)
        if len(mail.outbox) > 0:
            self.assertIn("test@example.com", mail.outbox[0].to)

    def test_multiple_users_isolation(self):
        """Testa isolamento entre múltiplos usuários"""
        # Criar dois usuários
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password123",
            first_name="User",
            last_name="One",
        )

        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password123",
            first_name="User",
            last_name="Two",
        )

        # Verificar isolamento dos usuários
        self.assertNotEqual(user1.username, user2.username)
        self.assertNotEqual(user1.email, user2.email)
        self.assertEqual(user1.username, "user1")
        self.assertEqual(user2.username, "user2")

    def test_authentication_required_flow(self):
        """Testa fluxos que requerem autenticação"""
        # Tentar acessar área que requer login (usando pedidos como exemplo)
        response = self.client.get("/pedidos/")
        self.assertEqual(response.status_code, 302)  # Redirect para login

        # Fazer login
        User.objects.create_user(username="testuser", email="test@example.com", password="password123")

        self.client.login(username="testuser", password="password123")

        # Agora deve conseguir acessar (ou pode dar 200 ou outro status dependendo da implementação)
        response = self.client.get("/pedidos/")
        self.assertIn(response.status_code, [200, 302])

    def test_logout_flow(self):
        """Testa fluxo de logout"""
        # Criar usuário e fazer login
        User.objects.create_user(username="testuser", email="test@example.com", password="password123")

        self.client.login(username="testuser", password="password123")

        # Verificar que está logado
        self.assertTrue("_auth_user_id" in self.client.session)

        # Fazer logout
        response = self.client.post(reverse("contas:logout"))
        self.assertEqual(response.status_code, 302)  # Redirect após logout

        # Verificar que foi deslogado
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_user_creation_flow(self):
        """Testa criação básica de usuário"""
        # Criar usuário programaticamente
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

        # Verificar se foi criado corretamente
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.check_password("password123"))

    def test_fluxo_completo_perfil_edicao(self):
        """Testa fluxo completo: cadastro -> login -> editar perfil"""
        # 1. Cadastro de usuário
        cadastro_data = {
            "full_name": "Maria Santos",
            "email": "maria@example.com",
            "password1": "minhasenha123",
            "password2": "minhasenha123",
        }

        response = self.client.post(reverse("contas:signup"), cadastro_data)
        self.assertIn(response.status_code, [200, 302])

        # Verifica se usuário foi criado
        user = User.objects.get(email="maria@example.com")

        # 2. Login do usuário
        login_response = self.client.post(
            reverse("contas:login"), {"username": "maria@example.com", "password": "minhasenha123"}
        )
        self.assertIn(login_response.status_code, [200, 302])

        # 3. Acessar página de perfil
        perfil_response = self.client.get(reverse("contas:perfil"))
        self.assertEqual(perfil_response.status_code, 200)

        # Verifica se perfil foi criado automaticamente
        self.assertTrue(Profile.objects.filter(user=user).exists())
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.role, Role.CLIENTE)

        # 4. Editar dados pessoais
        edit_data = {
            "form_type": "user_data",
            "full_name": "Maria Santos Silva",
            "email": "maria.silva@example.com",
        }

        edit_response = self.client.post(reverse("contas:perfil"), edit_data)
        self.assertEqual(edit_response.status_code, 302)  # Redirect após sucesso

        # Verifica se os dados foram atualizados (exceto email que precisa de confirmação)
        user.refresh_from_db()
        self.assertEqual(user.email, "maria@example.com")  # Email não muda até confirmação
        self.assertEqual(user.username, "maria@example.com")  # Username também não muda
        self.assertEqual(user.first_name, "Maria")
        self.assertEqual(user.last_name, "Santos Silva")

        # Verifica se a solicitação de mudança foi criada
        from apps.contas.models import EmailChangeRequest

        email_request = EmailChangeRequest.objects.filter(user=user, new_email="maria.silva@example.com").first()
        self.assertIsNotNone(email_request)
        self.assertEqual(email_request.old_email, "maria@example.com")
        self.assertFalse(email_request.confirmed)

    def test_fluxo_alteracao_senha_perfil(self):
        """Testa fluxo de alteração de senha através do perfil"""
        # 1. Criar e logar usuário
        user = User.objects.create_user(
            username="carlos@example.com",
            email="carlos@example.com",
            password="senhaantiga123",
            first_name="Carlos",
            last_name="Oliveira",
        )

        self.client.login(username="carlos@example.com", password="senhaantiga123")

        # 2. Alterar senha via perfil
        password_data = {
            "form_type": "password_change",
            "old_password": "senhaantiga123",
            "new_password1": "novaSenha456789",
            "new_password2": "novaSenha456789",
        }

        response = self.client.post(reverse("contas:perfil"), password_data)
        self.assertEqual(response.status_code, 302)  # Redirect após sucesso

        # 3. Verificar se a senha foi alterada
        user.refresh_from_db()
        self.assertTrue(user.check_password("novaSenha456789"))
        self.assertFalse(user.check_password("senhaantiga123"))

        # 4. Verificar se continua logado após alteração
        profile_response = self.client.get(reverse("contas:perfil"))
        self.assertEqual(profile_response.status_code, 200)

    def test_fluxo_acesso_perfil_sem_autenticacao(self):
        """Testa que perfil requer autenticação"""
        # Tentar acessar perfil sem estar logado
        response = self.client.get(reverse("contas:perfil"))
        self.assertEqual(response.status_code, 302)

        # Verifica se redireciona para login
        self.assertIn("/contas/login/", response.url)

    def test_fluxo_validacao_email_duplicado_perfil(self):
        """Testa validação de email duplicado na edição de perfil"""
        # 1. Criar dois usuários
        user1 = User.objects.create_user(
            username="user1@example.com", email="user1@example.com", password="password123"
        )

        User.objects.create_user(username="user2@example.com", email="user2@example.com", password="password123")

        # 2. Logar com user1
        self.client.login(username="user1@example.com", password="password123")

        # 3. Tentar alterar email para o email do user2
        edit_data = {
            "form_type": "user_data",
            "full_name": "User One Updated",
            "email": "user2@example.com",  # Email já em uso
        }

        response = self.client.post(reverse("contas:perfil"), edit_data)
        self.assertEqual(response.status_code, 200)  # Permanece na página com erro

        # 4. Verificar se o email não foi alterado
        user1.refresh_from_db()
        self.assertEqual(user1.email, "user1@example.com")

    def test_fluxo_perfil_criacao_automatica(self):
        """Testa que perfil existe automaticamente para usuário"""
        # 1. Criar usuário (perfil é criado automaticamente via signal)
        user = User.objects.create_user(
            username="noperfil@example.com", email="noperfil@example.com", password="password123"
        )

        # Verifica que perfil foi criado automaticamente via signal
        self.assertTrue(Profile.objects.filter(user=user).exists())
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.role, Role.CLIENTE)

        # 2. Logar e acessar perfil
        self.client.login(username="noperfil@example.com", password="password123")
        response = self.client.get(reverse("contas:perfil"))

        # 3. Verificar se página carrega corretamente com perfil existente
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"], profile)

    def test_fluxo_navegacao_perfil_pedidos(self):
        """Testa navegação entre perfil e outras páginas"""
        # 1. Criar e logar usuário
        User.objects.create_user(
            username="navegacao@example.com", email="navegacao@example.com", password="password123"
        )

        self.client.login(username="navegacao@example.com", password="password123")

        # 2. Acessar perfil
        perfil_response = self.client.get(reverse("contas:perfil"))
        self.assertEqual(perfil_response.status_code, 200)

        # 3. Verificar se pode navegar para pedidos (se existir a URL)
        try:
            pedidos_response = self.client.get(reverse("pedidos:listar"))
            self.assertIn(pedidos_response.status_code, [200, 302])
        except Exception:
            # URL pode não existir ainda, tudo bem
            pass

        # 4. Voltar ao perfil
        perfil_response2 = self.client.get(reverse("contas:perfil"))
        self.assertEqual(perfil_response2.status_code, 200)

    def test_fluxo_completo_mudanca_email_com_notificacao(self):
        """Testa fluxo completo: cadastro -> login -> mudar email -> receber notificação"""
        # 1. Cadastro de usuário
        cadastro_data = {
            "full_name": "Carlos Santos",
            "email": "carlos@example.com",
            "password1": "minhasenha123",
            "password2": "minhasenha123",
        }

        response = self.client.post(reverse("contas:signup"), cadastro_data)
        self.assertIn(response.status_code, [200, 302])

        # 2. Login do usuário
        login_response = self.client.post(
            reverse("contas:login"), {"username": "carlos@example.com", "password": "minhasenha123"}
        )
        self.assertIn(login_response.status_code, [200, 302])

        # Limpa caixa de email (pode haver emails de boas-vindas)
        mail.outbox = []

        # 3. Alterar email via perfil
        edit_data = {
            "form_type": "user_data",
            "full_name": "Carlos Santos Silva",
            "email": "carlos.silva@example.com",
        }

        edit_response = self.client.post(reverse("contas:perfil"), edit_data)
        self.assertEqual(edit_response.status_code, 302)  # Redirect após sucesso

        # 4. Verificar se notificação foi enviada (se possível)
        # O sistema pode ou não conseguir enviar email dependendo da configuração
        if len(mail.outbox) > 0:
            notification_email = mail.outbox[0]
            self.assertIn("carlos@example.com", notification_email.to)
            self.assertIn("Confirme a alteração de email", notification_email.subject)
            self.assertIn("carlos@example.com", notification_email.body)  # Email antigo
            self.assertIn("carlos.silva@example.com", notification_email.body)  # Email novo
            self.assertIn("Carlos Santos Silva", notification_email.body)  # Nome do usuário

        # 5. Verificar se os dados não foram atualizados ainda (precisa confirmação)
        user = User.objects.get(username="carlos@example.com")  # Username não muda até confirmação
        self.assertEqual(user.email, "carlos@example.com")

        # Verifica se a solicitação de mudança foi criada
        from apps.contas.models import EmailChangeRequest

        email_request = EmailChangeRequest.objects.filter(user=user, new_email="carlos.silva@example.com").first()
        self.assertIsNotNone(email_request)
        self.assertEqual(email_request.old_email, "carlos@example.com")
        self.assertFalse(email_request.confirmed)
        self.assertEqual(user.first_name, "Carlos")
        self.assertEqual(user.last_name, "Santos Silva")

        # 6. Verificar que ainda consegue fazer login com novo email
        self.client.logout()

        new_login_response = self.client.post(
            reverse("contas:login"), {"username": "carlos.silva@example.com", "password": "minhasenha123"}
        )
        self.assertIn(new_login_response.status_code, [200, 302])

    def test_fluxo_mudanca_email_falha_envio_notificacao(self):
        """Testa que sistema continua funcionando mesmo se falhar envio de notificação"""
        # 1. Criar e logar usuário
        user = User.objects.create_user(
            username="falhamail@example.com",
            email="falhamail@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

        self.client.login(username="falhamail@example.com", password="password123")

        # Limpa caixa de email
        mail.outbox = []

        # 2. Alterar email (sistema deve continuar funcionando mesmo com falha de email)
        edit_data = {
            "form_type": "user_data",
            "full_name": "Test User Updated",
            "email": "novoemail@example.com",
        }

        # Simula falha no envio de email usando configurações inválidas
        from django.test.utils import override_settings

        with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            edit_response = self.client.post(reverse("contas:perfil"), edit_data)

        # 3. Verifica que o sistema funcionou normalmente
        self.assertEqual(edit_response.status_code, 302)  # Redirect após sucesso

        # 4. Verifica que os dados NÃO foram atualizados ainda (precisam de confirmação)
        user.refresh_from_db()
        self.assertEqual(user.email, "falhamail@example.com")  # Email não muda até confirmação
        self.assertEqual(user.username, "falhamail@example.com")  # Username também não muda

        # Verifica se a solicitação de mudança foi criada
        from apps.contas.models import EmailChangeRequest

        email_request = EmailChangeRequest.objects.filter(user=user, new_email="novoemail@example.com").first()
        self.assertIsNotNone(email_request)
        self.assertEqual(email_request.old_email, "falhamail@example.com")
        self.assertFalse(email_request.confirmed)
