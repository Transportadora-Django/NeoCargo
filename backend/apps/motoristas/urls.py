"""URLs para o app motoristas."""

from django.urls import path
from . import views

app_name = "motoristas"

urlpatterns = [
    path("dashboard/", views.dashboard_motorista, name="dashboard"),
    path("entregas/historico/", views.historico_entregas, name="historico_entregas"),
    path("entregas/<int:atribuicao_id>/iniciar/", views.iniciar_entrega, name="iniciar_entrega"),
    path("entregas/<int:atribuicao_id>/concluir/", views.concluir_entrega, name="concluir_entrega"),
    path("entregas/<int:atribuicao_id>/relatar-problema/", views.relatar_problema, name="relatar_problema"),
    path("problemas/", views.meus_problemas, name="meus_problemas"),
]
