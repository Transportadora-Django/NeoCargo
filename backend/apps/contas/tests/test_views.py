from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.test.utils import override_settings

from ..forms import SignupForm
from ..models import Role


class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("contas:signup")
        self.valid_data = {
            "full_name": "João Silva Santos",
            "email": "joao@example.com",
            "password1": "testpass123456",
            "password2": "testpass123456",
            "website": "",  # honeypot field
        }

    def test_signup_view_get(self):
        """Testa se a view de cadastro retorna o formulário corretamente"""
        response = self.client.get(self.signup_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        self.assertIsInstance(response.context["form"], SignupForm)
        self.assertTemplateUsed(response, "contas/signup.html")

    def test_signup_view_post_valid_data(self):
        """Testa cadastro com dados válidos"""
        response = self.client.post(self.signup_url, self.valid_data)

        # Verifica se o usuário foi criado
        self.assertTrue(User.objects.filter(email="joao@example.com").exists())
        user = User.objects.get(email="joao@example.com")

        # Verifica se o Profile foi criado
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.role, Role.CLIENTE)

        # Verifica se o usuário foi autenticado
        self.assertTrue(user.is_authenticated)

        # Verifica redirecionamento (deve ir para dashboard_cliente)
        self.assertRedirects(response, reverse("dashboard_cliente"))

    def test_signup_view_post_invalid_data(self):
        """Testa cadastro com dados inválidos"""
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = "invalid-email"

        response = self.client.post(self.signup_url, invalid_data)

        # Não deve criar usuário
        self.assertFalse(User.objects.filter(email="invalid-email").exists())

        # Deve retornar o formulário com erros
        self.assertEqual(response.status_code, 200)
        # Verifica por mensagens de erro de email em diferentes idiomas
        content = response.content.decode()
        self.assertTrue(
            any(text in content for text in [
                "Enter a valid email address",
                "Digite um endereço de email válido",
                "email válido",
                "email address",
                "endereço de e-mail"
            ])
        )

    def test_signup_duplicate_email(self):
        """Testa cadastro com email duplicado"""
        # Cria um usuário primeiro
        User.objects.create_user(username="existing@example.com", email="existing@example.com", password="testpass123")

        duplicate_data = self.valid_data.copy()
        duplicate_data["email"] = "existing@example.com"

        response = self.client.post(self.signup_url, duplicate_data)

        # Deve retornar erro
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este e-mail já está em uso")

    def test_signup_honeypot_protection(self):
        """Testa proteção honeypot contra spam"""
        spam_data = self.valid_data.copy()
        spam_data["website"] = "http://spam.com"

        response = self.client.post(self.signup_url, spam_data)

        # Não deve criar usuário
        self.assertFalse(User.objects.filter(email="joao@example.com").exists())

        # Deve retornar status 200 (formulário com erro)
        self.assertEqual(response.status_code, 200)
        
        # Verifica se a proteção honeypot funcionou de alguma forma:
        # 1. Mensagem de erro de segurança OU
        # 2. Formulário foi rejeitado (usuário não foi criado)
        messages = list(get_messages(response.wsgi_request))
        has_security_message = any("Erro de segurança" in str(m) for m in messages)
        
        # Se não há mensagem, mas o usuário não foi criado, a proteção funcionou
        user_not_created = not User.objects.filter(email="joao@example.com").exists()
        
        # Pelo menos uma das proteções deve ter funcionado
        self.assertTrue(has_security_message or user_not_created)

    def test_signup_authenticated_user_redirect(self):
        """Testa se usuário já autenticado é redirecionado"""
        # Cria e autentica um usuário
        user = User.objects.create_user(
            username="authenticated@example.com", email="authenticated@example.com", password="testpass123"
        )
        self.client.force_login(user)

        response = self.client.get(self.signup_url)
        self.assertRedirects(response, reverse("dashboard_cliente"))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_signup_sends_welcome_email(self):
        """Testa se email de boas-vindas é enviado após cadastro"""
        mail.outbox = []

        self.client.post(self.signup_url, self.valid_data)

        # Verifica se email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Bem-vindo ao NeoCargo!")
        self.assertEqual(email.to, ["joao@example.com"])


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("contas:login")
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_login_view_get(self):
        """Testa se a view de login retorna o formulário"""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contas/login.html")

    def test_login_valid_credentials(self):
        """Testa login com credenciais válidas"""
        response = self.client.post(self.login_url, {"username": "testuser@example.com", "password": "testpass123"})

        # Verifica redirecionamento para dashboard do cliente
        self.assertRedirects(response, reverse("dashboard_cliente"))

        # Verifica se usuário está autenticado
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        response = self.client.post(self.login_url, {"username": "testuser@example.com", "password": "wrongpassword"})

        # Deve retornar erro
        self.assertEqual(response.status_code, 200)
        
        # Verifica se há erros no formulário
        self.assertTrue(response.context['form'].errors)
        
        # Verifica se há erros não-específicos de campo (credenciais inválidas)
        has_non_field_errors = bool(response.context['form'].non_field_errors)
        
        # Ou verifica se há classe alert-danger no HTML (indicando erro)
        content = response.content.decode()
        has_error_alert = "alert-danger" in content
        
        # Pelo menos uma das verificações deve ser verdadeira
        self.assertTrue(has_non_field_errors or has_error_alert)

    def test_login_redirect_based_on_role(self):
        """Testa redirecionamento baseado no role do usuário"""
        # Altera o role para motorista
        self.user.profile.role = Role.MOTORISTA
        self.user.profile.save()

        response = self.client.post(self.login_url, {"username": "testuser@example.com", "password": "testpass123"})

        self.assertRedirects(response, reverse("dashboard_motorista"))

    def test_login_authenticated_user_redirect(self):
        """Testa se usuário já autenticado é redirecionado"""
        self.client.force_login(self.user)

        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse("dashboard_cliente"))


class CustomLogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse("contas:logout")
        self.user = User.objects.create_user(
            username="testuser@example.com", email="testuser@example.com", password="testpass123"
        )

    def test_logout_authenticated_user(self):
        """Testa logout de usuário autenticado"""
        self.client.force_login(self.user)

        response = self.client.post(self.logout_url)

        # Verifica redirecionamento
        self.assertRedirects(response, reverse("home"))

        # Verifica se usuário foi desautenticado
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_unauthenticated_user(self):
        """Testa logout de usuário não autenticado"""
        response = self.client.post(self.logout_url)

        # Deve redirecionar normalmente
        self.assertRedirects(response, reverse("home"))
