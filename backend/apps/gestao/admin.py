from django.contrib import admin
from .models import ConfiguracaoSistema, SolicitacaoMudancaPerfil


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ["solicitacoes_abertas", "atualizado_em", "atualizado_por"]
    fieldsets = (
        ("Status das Solicitações", {"fields": ("solicitacoes_abertas", "mensagem_solicitacoes_fechadas")}),
        ("Informações", {"fields": ("atualizado_em", "atualizado_por"), "classes": ("collapse",)}),
    )
    readonly_fields = ("atualizado_em",)

    def has_add_permission(self, request):
        # Permite apenas uma configuração
        return not ConfiguracaoSistema.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Não permite deletar a configuração
        return False


@admin.register(SolicitacaoMudancaPerfil)
class SolicitacaoMudancaPerfilAdmin(admin.ModelAdmin):
    list_display = ["usuario", "role_atual", "role_solicitada", "status", "created_at"]
    list_filter = ["status", "role_atual", "role_solicitada", "created_at"]
    search_fields = ["usuario__username", "usuario__first_name", "usuario__last_name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("usuario", "role_atual", "role_solicitada", "justificativa")}),
        ("Dados Pessoais", {"fields": ("telefone", "cpf", "endereco", "data_nascimento"), "classes": ("collapse",)}),
        (
            "Dados do Veículo",
            {
                "fields": ("tipo_veiculo", "modelo_veiculo", "placa_veiculo", "ano_veiculo", "cor_veiculo"),
                "classes": ("collapse",),
            },
        ),
        ("Aprovação", {"fields": ("status", "observacoes_admin", "aprovado_por", "data_aprovacao")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
