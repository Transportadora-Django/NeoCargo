from django.test import TestCase
from django.contrib.auth.models import User
from apps.pedidos.forms import PedidoForm


class PedidoFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_form_valido(self):
        """Testa formulário com dados válidos"""
        form_data = {
            "cidade_origem": "São Paulo",
            "cidade_destino": "Rio de Janeiro",
            "peso_carga": "100.50",
            "prazo_desejado": 7,
            "observacoes": "Carga frágil",
        }
        form = PedidoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_sem_observacoes(self):
        """Testa formulário sem observações (campo opcional)"""
        form_data = {
            "cidade_origem": "São Paulo",
            "cidade_destino": "Rio de Janeiro",
            "peso_carga": "100.50",
            "prazo_desejado": 7,
        }
        form = PedidoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_campos_obrigatorios(self):
        """Testa validação de campos obrigatórios"""
        form = PedidoForm(data={})
        self.assertFalse(form.is_valid())

        # Verifica se os campos obrigatórios estão nos erros
        required_fields = ["cidade_origem", "cidade_destino", "peso_carga", "prazo_desejado"]
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_peso_invalido(self):
        """Testa peso inválido"""
        form_data = {
            "cidade_origem": "São Paulo",
            "cidade_destino": "Rio de Janeiro",
            "peso_carga": "0",  # Peso zero não é válido
            "prazo_desejado": 7,
        }
        form = PedidoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("peso_carga", form.errors)

    def test_prazo_invalido(self):
        """Testa prazo inválido"""
        form_data = {
            "cidade_origem": "São Paulo",
            "cidade_destino": "Rio de Janeiro",
            "peso_carga": "100.50",
            "prazo_desejado": 0,  # Prazo zero não é válido
        }
        form = PedidoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("prazo_desejado", form.errors)
