from django.contrib import admin
from .models import Motorista, AtribuicaoPedido


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ["get_nome", "sede_atual", "cnh_categoria", "disponivel", "entregas_concluidas"]
    list_filter = ["disponivel", "cnh_categoria", "sede_atual"]
    search_fields = ["profile__user__username", "profile__user__first_name", "profile__user__last_name"]
    readonly_fields = ["entregas_concluidas", "created_at", "updated_at"]

    def get_nome(self, obj):
        return obj.profile.user.get_full_name() or obj.profile.user.username

    get_nome.short_description = "Nome"


@admin.register(AtribuicaoPedido)
class AtribuicaoPedidoAdmin(admin.ModelAdmin):
    list_display = ["pedido", "motorista", "veiculo", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["pedido__id", "motorista__profile__user__username", "veiculo__placa"]
    readonly_fields = ["created_at", "updated_at"]
