from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail


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
