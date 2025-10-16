from django.urls import path
from . import views

app_name = "veiculos"

urlpatterns = [
    # Especificações
    path("especificacoes/", views.listar_especificacoes, name="listar_especificacoes"),
    path("especificacoes/adicionar/", views.adicionar_especificacao, name="adicionar_especificacao"),
    path("especificacoes/<int:especificacao_id>/editar/", views.editar_especificacao, name="editar_especificacao"),
    path("especificacoes/<int:especificacao_id>/remover/", views.remover_especificacao, name="remover_especificacao"),
    # Veículos
    path("", views.listar_veiculos, name="listar_veiculos"),
    path("adicionar/", views.adicionar_veiculo, name="adicionar_veiculo"),
    path("<int:veiculo_id>/editar/", views.editar_veiculo, name="editar_veiculo"),
    path("<int:veiculo_id>/remover/", views.remover_veiculo, name="remover_veiculo"),
]
