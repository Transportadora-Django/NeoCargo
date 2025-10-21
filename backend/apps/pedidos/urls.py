from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    path("criar/", views.pedido_criar, name="criar"),
    path("<int:pedido_id>/cotacao/", views.gerar_cotacao, name="gerar_cotacao"),
    path("<int:pedido_id>/confirmar/", views.confirmar_pedido, name="confirmar"),
    path("<int:pedido_id>/cancelar/", views.cancelar_pedido, name="cancelar"),
    path("api/destinos-disponiveis/", views.api_destinos_disponiveis, name="api_destinos_disponiveis"),
    path("", views.pedido_listar, name="listar"),
]
