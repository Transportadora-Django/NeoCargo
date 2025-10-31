from django.contrib import admin
from .models import Motorista, AtribuicaoPedido, ProblemaEntrega


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


@admin.register(ProblemaEntrega)
class ProblemaEntregaAdmin(admin.ModelAdmin):
    list_display = ["get_pedido_id", "tipo", "status", "get_motorista", "criado_em"]
    list_filter = ["status", "tipo", "criado_em"]
    search_fields = ["atribuicao__pedido__id", "atribuicao__motorista__profile__user__username", "descricao"]
    readonly_fields = ["criado_em", "atualizado_em"]
    fieldsets = (
        ("Informações Básicas", {"fields": ("atribuicao", "tipo", "status")}),
        ("Descrição", {"fields": ("descricao",)}),
        ("Resolução", {"fields": ("resolucao", "resolvido_em")}),
        ("Datas", {"fields": ("criado_em", "atualizado_em")}),
    )

    def get_pedido_id(self, obj):
        return f"Pedido #{obj.atribuicao.pedido.id}"

    get_pedido_id.short_description = "Pedido"

    def get_motorista(self, obj):
        return obj.atribuicao.motorista.profile.user.get_full_name() or obj.atribuicao.motorista.profile.user.username

    get_motorista.short_description = "Motorista"
