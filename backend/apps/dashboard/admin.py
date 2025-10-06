from django.contrib import admin
from .models import SolicitacaoMudancaPerfil


@admin.register(SolicitacaoMudancaPerfil)
class SolicitacaoMudancaPerfilAdmin(admin.ModelAdmin):
    list_display = ["user", "perfil_atual", "perfil_solicitado", "status", "created_at"]
    list_filter = ["status", "perfil_atual", "perfil_solicitado", "created_at"]
    search_fields = ["user__username", "user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Informações da Solicitação", {"fields": ("user", "perfil_atual", "perfil_solicitado", "justificativa")}),
        ("Status", {"fields": ("status", "aprovada_por", "observacoes_aprovacao")}),
        ("Datas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ["user", "perfil_atual", "perfil_solicitado"]
        return self.readonly_fields
