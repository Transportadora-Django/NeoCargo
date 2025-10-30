"""
Admin para gerenciamento de cidades e rotas.
"""

from django.contrib import admin
from .models import Cidade, Rota


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    """Admin para Cidade."""

    list_display = ["nome", "estado", "latitude", "longitude", "ativa", "created_at"]
    list_filter = ["estado", "ativa"]
    search_fields = ["nome", "estado"]
    ordering = ["estado", "nome"]
    list_per_page = 50


@admin.register(Rota)
class RotaAdmin(admin.ModelAdmin):
    """Admin para Rota."""

    list_display = ["origem", "destino", "distancia_km", "tempo_estimado_horas", "pedagio_valor", "ativa", "created_at"]
    list_filter = ["ativa", "origem__estado", "destino__estado"]
    search_fields = ["origem__nome", "destino__nome"]
    ordering = ["origem__nome", "destino__nome"]
    list_per_page = 50
    raw_id_fields = ["origem", "destino"]
