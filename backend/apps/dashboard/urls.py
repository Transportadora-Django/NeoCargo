from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("cliente/", views.dashboard_cliente, name="cliente"),
    path("solicitar-mudanca-perfil/", views.solicitar_mudanca_perfil, name="solicitar_mudanca_perfil"),
]
