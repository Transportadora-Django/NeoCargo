from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    path("criar/", views.pedido_criar, name="criar"),
    path("<int:pedido_id>/cancelar/", views.cancelar_pedido, name="cancelar"),
    path("", views.pedido_listar, name="listar"),
]
