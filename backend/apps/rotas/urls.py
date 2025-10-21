"""
URLs para o app Rotas.
"""

from django.urls import path
from . import views

app_name = "rotas"

urlpatterns = [
    # Públicas
    path("", views.mapa_rotas, name="mapa"),
    path("cidades/", views.listar_cidades_publico, name="cidades_publico"),
    path("lista/", views.listar_rotas_publico, name="listar_rotas_publico"),
    # Gestão (Owner/Gerente)
    path("gerenciar/", views.dashboard_rotas, name="dashboard_rotas"),
    path("gerenciar/cidades/", views.listar_cidades, name="listar_cidades"),
    path("gerenciar/cidades/nova/", views.criar_cidade, name="criar_cidade"),
    path("gerenciar/cidades/<int:cidade_id>/editar/", views.editar_cidade, name="editar_cidade"),
    path("gerenciar/rotas/", views.listar_rotas, name="listar_rotas"),
    path("gerenciar/rotas/nova/", views.criar_rota, name="criar_rota"),
    path("gerenciar/rotas/<int:rota_id>/editar/", views.editar_rota, name="editar_rota"),
    path("gerenciar/precos/", views.configurar_precos, name="configurar_precos"),
]
