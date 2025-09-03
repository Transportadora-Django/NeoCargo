from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.test.utils import override_settings

from ..models import Profile, Role


class SignalsTest(TestCase):
    def test_profile_created_on_user_creation(self):
        """Testa se o Profile é criado automaticamente quando um User é criado"""
        user = User.objects.create_user(
            username="testuser@example.com", email="testuser@example.com", password="testpass123"
        )

        # Verifica se o Profile foi criado
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(user.profile.role, Role.CLIENTE)

    def test_profile_not_duplicated_on_user_save(self):
        """Testa se um novo Profile não é criado quando o User é salvo novamente"""
        user = User.objects.create_user(
            username="testuser@example.com", email="testuser@example.com", password="testpass123"
        )

        # Verifica se existe apenas um Profile
        profile_count_before = Profile.objects.filter(user=user).count()
        self.assertEqual(profile_count_before, 1)

        # Salva o usuário novamente
        user.first_name = "Test"
        user.save()

        # Verifica se ainda existe apenas um Profile
        profile_count_after = Profile.objects.filter(user=user).count()
        self.assertEqual(profile_count_after, 1)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="test@neocargo.local"
    )
    def test_welcome_email_sent_on_user_creation(self):
        """Testa se o email de boas-vindas é enviado quando um usuário é criado"""
        # Limpa a caixa de emails de teste
        mail.outbox = []

        User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Verifica se um email foi enviado
        self.assertEqual(len(mail.outbox), 1)

        # Verifica o conteúdo do email
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Bem-vindo ao NeoCargo!")
        self.assertEqual(email.to, ["testuser@example.com"])
        self.assertEqual(email.from_email, "test@neocargo.local")
        self.assertIn("Test User", email.body)
        self.assertIn("Seja bem-vindo ao NeoCargo", email.body)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_welcome_email_uses_username_when_no_full_name(self):
        """Testa se o email usa o username quando não há nome completo"""
        mail.outbox = []

        User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="testpass123")

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("testuser@example.com", email.body)

    def test_profile_role_can_be_changed(self):
        """Testa se o role do Profile pode ser alterado"""
        user = User.objects.create_user(
            username="testuser@example.com", email="testuser@example.com", password="testpass123"
        )

        # Verifica role inicial
        self.assertEqual(user.profile.role, Role.CLIENTE)

        # Altera o role
        user.profile.role = Role.MOTORISTA
        user.profile.save()

        # Recarrega do banco
        user.refresh_from_db()
        self.assertEqual(user.profile.role, Role.MOTORISTA)

    def test_multiple_users_get_profiles(self):
        """Testa se múltiplos usuários recebem seus Profiles"""
        users_data = [
            ("user1@example.com", "User", "One"),
            ("user2@example.com", "User", "Two"),
            ("user3@example.com", "User", "Three"),
        ]

        users = []
        for email, first_name, last_name in users_data:
            user = User.objects.create_user(
                username=email, email=email, password="testpass123", first_name=first_name, last_name=last_name
            )
            users.append(user)

        # Verifica se todos os usuários têm Profile
        for user in users:
            self.assertTrue(hasattr(user, "profile"))
            self.assertEqual(user.profile.role, Role.CLIENTE)
