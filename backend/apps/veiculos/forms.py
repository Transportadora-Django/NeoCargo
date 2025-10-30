from django import forms
from .models import EspecificacaoVeiculo, Veiculo


class EspecificacaoVeiculoForm(forms.ModelForm):
    """Formulário para cadastro e edição de especificações de veículos"""

    class Meta:
        model = EspecificacaoVeiculo
        fields = [
            "tipo",
            "combustivel_principal",
            "combustivel_alternativo",
            "rendimento_principal",
            "rendimento_alternativo",
            "carga_maxima",
            "velocidade_media",
            "reducao_rendimento_principal",
            "reducao_rendimento_alternativo",
        ]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "combustivel_principal": forms.Select(attrs={"class": "form-select"}),
            "combustivel_alternativo": forms.Select(attrs={"class": "form-select"}),
            "rendimento_principal": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "km/l"}
            ),
            "rendimento_alternativo": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "km/l (opcional)"}
            ),
            "carga_maxima": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "kg"}),
            "velocidade_media": forms.NumberInput(attrs={"class": "form-control", "placeholder": "km/h"}),
            "reducao_rendimento_principal": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.0001", "placeholder": "0.001"}
            ),
            "reducao_rendimento_alternativo": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.0001", "placeholder": "0.001 (opcional)"}
            ),
        }
        labels = {
            "tipo": "Tipo de Veículo",
            "combustivel_principal": "Combustível Principal",
            "combustivel_alternativo": "Combustível Alternativo",
            "rendimento_principal": "Rendimento Principal (km/l)",
            "rendimento_alternativo": "Rendimento Alternativo (km/l)",
            "carga_maxima": "Carga Máxima (kg)",
            "velocidade_media": "Velocidade Média (km/h)",
            "reducao_rendimento_principal": "Redução de Rendimento Principal",
            "reducao_rendimento_alternativo": "Redução de Rendimento Alternativo",
        }
        help_texts = {
            "reducao_rendimento_principal": "Redução por kg de carga (ex: 0.001)",
            "reducao_rendimento_alternativo": "Redução por kg de carga (ex: 0.001)",
        }


class VeiculoForm(forms.ModelForm):
    """Formulário para cadastro de veículos da empresa"""

    class Meta:
        model = Veiculo
        fields = ["especificacao", "marca", "modelo", "placa", "ano", "cor", "sede_atual", "ativo"]
        widgets = {
            "especificacao": forms.Select(attrs={"class": "form-select"}),
            "marca": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Ford, Scania, Honda"}),
            "modelo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Transit, R450, CG 160"}),
            "placa": forms.TextInput(attrs={"class": "form-control", "placeholder": "ABC-1234"}),
            "ano": forms.NumberInput(attrs={"class": "form-control", "placeholder": "2024"}),
            "cor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Branco, Preto, Vermelho"}),
            "sede_atual": forms.Select(attrs={"class": "form-select"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "especificacao": "Tipo de Veículo",
            "marca": "Marca",
            "modelo": "Modelo",
            "placa": "Placa",
            "ano": "Ano de Fabricação",
            "cor": "Cor",
            "sede_atual": "Sede Atual (Cidade)",
            "ativo": "Veículo Ativo",
        }
