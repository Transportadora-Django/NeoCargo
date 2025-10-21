from django import forms
from django.db import models
from .models import Pedido, OpcaoCotacao


class PedidoForm(forms.ModelForm):
    """Formulário para gerar cotação de pedido"""

    # Sobrescrever os campos de cidade para usar ChoiceField
    cidade_origem = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-select", "id": "id_cidade_origem"}),
        label="Cidade de Origem",
        required=True
    )

    cidade_destino = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-select", "id": "id_cidade_destino"}),
        label="Cidade de Destino",
        required=True
    )

    # Campo para escolher a opção após ver as cotações
    opcao_escolhida = forms.ChoiceField(
        choices=[("", "Selecione uma opção")] + list(OpcaoCotacao.choices),
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Escolha a melhor opção para você",
    )

    class Meta:
        model = Pedido
        fields = ["cidade_origem", "cidade_destino", "peso_carga", "prazo_desejado", "observacoes"]
        widgets = {
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Importar aqui para evitar circular import
        from apps.rotas.models import Cidade

        # Buscar apenas cidades ativas que têm rotas (origem ou destino)
        cidades_com_rotas = (
            Cidade.objects.filter(ativa=True)
            .filter(models.Q(rotas_origem__ativa=True) | models.Q(rotas_destino__ativa=True))
            .distinct()
            .order_by("estado", "nome")
        )

        # Criar choices para o select (formato: "Cidade - Estado")
        cidade_choices = [("", "Selecione uma cidade")]

        for cidade in cidades_com_rotas:
            # Usar formato "Cidade - Estado" para exibição e valor
            label = f"{cidade.nome} - {cidade.get_estado_display()}"
            cidade_choices.append((label, label))

        # Atualizar as choices dos campos
        self.fields["cidade_origem"].choices = cidade_choices
        self.fields["cidade_destino"].choices = cidade_choices

    def clean(self):
        cleaned_data = super().clean()
        origem = cleaned_data.get("cidade_origem")
        destino = cleaned_data.get("cidade_destino")

        if origem and destino and origem == destino:
            raise forms.ValidationError("A cidade de origem não pode ser igual à cidade de destino.")

        # Verificar se existe rota entre as cidades (formato: "Cidade - Estado")
        if origem and destino and " - " in origem and " - " in destino:
            from apps.rotas.models import Rota, Cidade

            try:
                # Parsear nome da cidade (formato: "São Paulo - São Paulo")
                origem_nome, origem_estado_nome = origem.rsplit(" - ", 1)
                destino_nome, destino_estado_nome = destino.rsplit(" - ", 1)

                # Buscar as cidades pelo nome e estado
                cidade_origem = Cidade.objects.filter(
                    nome=origem_nome.strip(),
                    ativa=True
                ).first()

                cidade_destino = Cidade.objects.filter(
                    nome=destino_nome.strip(),
                    ativa=True
                ).first()

                if not cidade_origem or not cidade_destino:
                    raise forms.ValidationError("Cidade não encontrada. Por favor, selecione uma cidade válida.")

                # Verificar se existe rota ativa
                rota = Rota.objects.filter(origem=cidade_origem, destino=cidade_destino, ativa=True).first()

                if not rota:
                    raise forms.ValidationError(
                        f"Não existe rota cadastrada entre {origem} e {destino}. "
                        "Entre em contato para verificar disponibilidade."
                    )

            except Exception:
                raise forms.ValidationError("Erro ao validar as cidades. Por favor, tente novamente.")

        return cleaned_data
