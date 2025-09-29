from django.contrib import admin
from .models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "cidade_origem", "cidade_destino", "peso_carga", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["cliente__username", "cliente__email", "cidade_origem", "cidade_destino", "observacoes"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Informações do Cliente", {"fields": ("cliente",)}),
        (
            "Dados da Carga",
            {"fields": ("cidade_origem", "cidade_destino", "peso_carga", "prazo_desejado", "observacoes")},
        ),
        ("Status", {"fields": ("status",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("cliente")
