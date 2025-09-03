from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from ..models import Profile, Role


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_profile_creation_with_default_role(self):
        """Testa se o Profile é criado com role padrão de cliente"""
        # O Profile deve ser criado automaticamente pelo signal
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertEqual(self.user.profile.role, Role.CLIENTE)

    def test_profile_str_method(self):
        """Testa o método __str__ do Profile"""
        expected = f"{self.user.get_full_name()} - Cliente"
        self.assertEqual(str(self.user.profile), expected)

    def test_profile_role_properties(self):
        """Testa as propriedades de role do Profile"""
        profile = self.user.profile

        # Teste role cliente (padrão)
        self.assertTrue(profile.is_cliente)
        self.assertFalse(profile.is_motorista)
        self.assertFalse(profile.is_gerente)
        self.assertFalse(profile.is_owner)

        # Teste role motorista
        profile.role = Role.MOTORISTA
        profile.save()
        self.assertFalse(profile.is_cliente)
        self.assertTrue(profile.is_motorista)
        self.assertFalse(profile.is_gerente)
        self.assertFalse(profile.is_owner)

        # Teste role gerente
        profile.role = Role.GERENTE
        profile.save()
        self.assertFalse(profile.is_cliente)
        self.assertFalse(profile.is_motorista)
        self.assertTrue(profile.is_gerente)
        self.assertFalse(profile.is_owner)

        # Teste role owner
        profile.role = Role.OWNER
        profile.save()
        self.assertFalse(profile.is_cliente)
        self.assertFalse(profile.is_motorista)
        self.assertFalse(profile.is_gerente)
        self.assertTrue(profile.is_owner)

    def test_one_to_one_relationship(self):
        """Testa a relação OneToOne entre User e Profile"""
        # Não deve ser possível criar outro Profile para o mesmo User
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user, role=Role.MOTORISTA)

    def test_profile_verbose_names(self):
        """Testa os verbose names do modelo"""
        profile = Profile._meta
        self.assertEqual(profile.verbose_name, "Perfil")
        self.assertEqual(profile.verbose_name_plural, "Perfis")

    def test_role_choices(self):
        """Testa as choices do campo role"""
        expected_choices = [
            ("cliente", "Cliente"),
            ("motorista", "Motorista"),
            ("gerente", "Gerente"),
            ("owner", "Owner"),
        ]
        self.assertEqual(Role.choices, expected_choices)
