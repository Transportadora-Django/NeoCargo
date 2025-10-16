from django.urls import path
from . import views

app_name = "gestao"

urlpatterns = [
    # Dashboard do dono
    path("dashboard/", views.dashboard_dono, name="dashboard_dono"),
    # Gestão de usuários
    path("usuarios/", views.listar_usuarios, name="listar_usuarios"),
    # Solicitações de mudança de perfil
    path("solicitar-mudanca/", views.solicitar_mudanca_perfil, name="solicitar_mudanca"),
    path("minhas-solicitacoes/", views.minhas_solicitacoes, name="minhas_solicitacoes"),
    path("solicitacoes/", views.listar_solicitacoes, name="listar_solicitacoes"),
    path("solicitacoes/<int:solicitacao_id>/aprovar/", views.aprovar_solicitacao, name="aprovar_solicitacao"),
    # Configurações
    path("toggle-solicitacoes/", views.toggle_solicitacoes, name="toggle_solicitacoes"),
]
