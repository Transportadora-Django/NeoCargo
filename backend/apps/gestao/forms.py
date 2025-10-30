from django import forms
from apps.contas.models import Profile, Role
from .models import SolicitacaoMudancaPerfil


class SolicitacaoMudancaPerfilForm(forms.ModelForm):
    """Formulário para solicitação de mudança de perfil"""

    class Meta:
        model = SolicitacaoMudancaPerfil
        fields = [
            "role_solicitada",
            "justificativa",
            "telefone",
            "cpf",
            "endereco",
            "data_nascimento",
            "cnh_categoria",
            "sede_atual",
        ]
        widgets = {
            "role_solicitada": forms.Select(attrs={"class": "form-select", "id": "id_role_solicitada"}),
            "justificativa": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Explique por que deseja mudar de perfil..."}
            ),
            "telefone": forms.TextInput(attrs={"class": "form-control", "placeholder": "(11) 99999-9999"}),
            "cpf": forms.TextInput(attrs={"class": "form-control", "placeholder": "000.000.000-00"}),
            "endereco": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Rua, número, bairro, cidade, CEP..."}
            ),
            "data_nascimento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "cnh_categoria": forms.Select(attrs={"class": "form-select"}),
            "sede_atual": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Define o role atual baseado no perfil do usuário
            try:
                perfil = user.profile
                self.fields["role_solicitada"].choices = self._get_available_roles(perfil.role)
                self.instance.role_atual = perfil.role
            except Profile.DoesNotExist:
                # Se não tem perfil, assume cliente
                self.fields["role_solicitada"].choices = self._get_available_roles(Role.CLIENTE)
                self.instance.role_atual = Role.CLIENTE

            self.instance.usuario = user

    def _get_available_roles(self, current_role):
        """Retorna os roles disponíveis baseado no role atual"""
        all_roles = Role.choices

        # Remove o role atual e o role de owner (que não pode ser solicitado)
        available = [(role, label) for role, label in all_roles if role != current_role and role != Role.OWNER]

        return [("", "Selecione um perfil...")] + available

    def clean(self):
        cleaned_data = super().clean()
        role_solicitada = cleaned_data.get("role_solicitada")

        # Validações - campos básicos são obrigatórios
        if role_solicitada:
            required_fields = ["telefone", "cpf", "endereco", "data_nascimento"]

            for field in required_fields:
                if not cleaned_data.get(field):
                    field_label = self.fields[field].label or field.replace("_", " ").title()
                    self.add_error(field, f"{field_label} é obrigatório.")

            # Se for motorista, CNH e sede são obrigatórios
            if role_solicitada == Role.MOTORISTA:
                if not cleaned_data.get("cnh_categoria"):
                    self.add_error("cnh_categoria", "Categoria CNH é obrigatória para motoristas.")
                if not cleaned_data.get("sede_atual"):
                    self.add_error("sede_atual", "Sede atual é obrigatória para motoristas.")

        return cleaned_data


class AprovarSolicitacaoForm(forms.ModelForm):
    """Formulário para aprovação/rejeição de solicitações"""

    class Meta:
        model = SolicitacaoMudancaPerfil
        fields = ["status", "observacoes_admin"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "observacoes_admin": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Observações sobre a decisão (opcional)..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apenas permite aprovação ou rejeição
        self.fields["status"].choices = [
            ("", "Selecione uma ação..."),
            ("aprovada", "Aprovar"),
            ("rejeitada", "Rejeitar"),
        ]
