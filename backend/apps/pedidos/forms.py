from django import forms
from .models import Pedido


class PedidoForm(forms.ModelForm):
    """Formulário para gerar cotação de pedido"""

    class Meta:
        model = Pedido
        fields = ["cidade_origem", "cidade_destino", "peso_carga", "prazo_desejado", "observacoes"]
        widgets = {
            "cidade_origem": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: São Paulo - SP"}),
            "cidade_destino": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Rio de Janeiro - RJ"}
            ),
            "peso_carga": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01", "min": "0.01"}
            ),
            "prazo_desejado": forms.NumberInput(attrs={"class": "form-control", "placeholder": "7", "min": "1"}),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Informações adicionais sobre a carga (opcional)",
                }
            ),
        }
