from django.contrib import admin
from .models import EspecificacaoVeiculo, Veiculo


@admin.register(EspecificacaoVeiculo)
class EspecificacaoVeiculoAdmin(admin.ModelAdmin):
    list_display = ["tipo", "combustivel_principal", "rendimento_principal", "carga_maxima", "velocidade_media"]
    list_filter = ["tipo", "combustivel_principal"]
    search_fields = ["tipo"]
    ordering = ["tipo"]


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ["placa", "marca", "modelo", "ano", "cor", "especificacao", "ativo", "created_at"]
    list_filter = ["ativo", "especificacao__tipo", "ano"]
    search_fields = ["placa", "marca", "modelo"]
    ordering = ["-created_at"]
    list_editable = ["ativo"]
