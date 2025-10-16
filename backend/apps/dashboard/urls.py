from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("cliente/", views.dashboard_cliente, name="cliente"),
]
