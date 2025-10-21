"""
Forms para gerenciamento de rotas e configurações.
"""

from django import forms
from .models import Cidade, Rota
from decimal import Decimal


class CidadeForm(forms.ModelForm):
    """Form para criar/editar cidade."""

    class Meta:
        model = Cidade
        fields = ["nome", "estado", "latitude", "longitude", "ativa"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: São Paulo"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "latitude": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: -23.5505199", "step": "0.0000001"}
            ),
            "longitude": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: -46.6333094", "step": "0.0000001"}
            ),
            "ativa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class RotaForm(forms.ModelForm):
    """Form para criar/editar rota."""

    class Meta:
        model = Rota
        fields = ["origem", "destino", "distancia_km", "tempo_estimado_horas", "pedagio_valor", "ativa", "observacoes"]
        widgets = {
            "origem": forms.Select(attrs={"class": "form-select"}),
            "destino": forms.Select(attrs={"class": "form-select"}),
            "distancia_km": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: 450.50", "step": "0.01"}
            ),
            "tempo_estimado_horas": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: 6.5", "step": "0.01"}
            ),
            "pedagio_valor": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: 45.00", "step": "0.01"}
            ),
            "ativa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observacoes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Observações sobre a rota (opcional)"}
            ),
        }


class ConfiguracaoPrecoForm(forms.Form):
    """Form para configurar preços de combustível e margem de lucro."""

    preco_alcool = forms.DecimalField(
        label="Preço do Álcool (R$/L)",
        max_digits=6,
        decimal_places=3,
        initial=Decimal("3.499"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "placeholder": "Ex: 3.499"}),
        help_text="Preço por litro de álcool",
    )

    preco_gasolina = forms.DecimalField(
        label="Preço da Gasolina (R$/L)",
        max_digits=6,
        decimal_places=3,
        initial=Decimal("4.449"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "placeholder": "Ex: 4.449"}),
        help_text="Preço por litro de gasolina",
    )

    preco_diesel = forms.DecimalField(
        label="Preço do Diesel (R$/L)",
        max_digits=6,
        decimal_places=3,
        initial=Decimal("3.869"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "placeholder": "Ex: 3.869"}),
        help_text="Preço por litro de diesel",
    )

    margem_lucro = forms.DecimalField(
        label="Margem de Lucro (%)",
        max_digits=5,
        decimal_places=2,
        initial=Decimal("20.00"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Ex: 20.00"}),
        help_text="Margem de lucro em porcentagem",
    )
