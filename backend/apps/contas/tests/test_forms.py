from django.test import TestCase
from django.contrib.auth.models import User

from ..forms import SignupForm


class SignupFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "full_name": "João Silva Santos",
            "email": "joao@example.com",
            "password1": "testpass123456",
            "password2": "testpass123456",
            "website": "",  # honeypot field
        }

    def test_signup_form_valid_data(self):
        """Testa se o formulário é válido com dados corretos"""
        form = SignupForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_signup_form_save_creates_user(self):
        """Testa se o método save cria o usuário corretamente"""
        form = SignupForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Verifica se o usuário foi criado
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "joao@example.com")
        self.assertEqual(user.username, "joao@example.com")
        self.assertEqual(user.first_name, "João")
        self.assertEqual(user.last_name, "Silva Santos")
        self.assertEqual(user.get_full_name(), "João Silva Santos")

    def test_email_normalization(self):
        """Testa se o email é normalizado (lowercase e trim)"""
        data = self.valid_data.copy()
        data["email"] = "  JOAO@EXAMPLE.COM  "

        form = SignupForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data["email"], "joao@example.com")

    def test_duplicate_email_validation(self):
        """Testa se emails duplicados são rejeitados"""
        # Cria um usuário primeiro
        User.objects.create_user(username="existing@example.com", email="existing@example.com", password="testpass123")

        data = self.valid_data.copy()
        data["email"] = "existing@example.com"

        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("Este e-mail já está em uso", str(form.errors["email"]))

    def test_full_name_validation(self):
        """Testa validação do nome completo"""
        # Nome com apenas uma palavra deve falhar
        data = self.valid_data.copy()
        data["full_name"] = "João"

        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)
        self.assertIn("nome completo", str(form.errors["full_name"]))

    def test_password_mismatch(self):
        """Testa se senhas diferentes são rejeitadas"""
        data = self.valid_data.copy()
        data["password2"] = "differentpassword"

        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_honeypot_field_validation(self):
        """Testa se o campo honeypot funciona como proteção anti-spam"""
        data = self.valid_data.copy()
        data["website"] = "http://spam.com"

        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("website", form.errors)
        self.assertIn("Spam detectado", str(form.errors["website"]))

    def test_required_fields(self):
        """Testa se todos os campos obrigatórios são validados"""
        required_fields = ["full_name", "email", "password1", "password2"]

        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ""

            form = SignupForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_form_field_attributes(self):
        """Testa se os campos têm os atributos CSS corretos"""
        form = SignupForm()

        # Verifica se os campos têm a classe CSS
        self.assertEqual(form.fields["full_name"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["email"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["password1"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["password2"].widget.attrs["class"], "form-control")

    def test_form_labels_in_portuguese(self):
        """Testa se os labels estão em português"""
        form = SignupForm()

        self.assertEqual(form.fields["full_name"].label, "Nome completo")
        self.assertEqual(form.fields["email"].label, "E-mail")
        self.assertEqual(form.fields["password1"].label, "Senha")
        self.assertEqual(form.fields["password2"].label, "Confirmar senha")
