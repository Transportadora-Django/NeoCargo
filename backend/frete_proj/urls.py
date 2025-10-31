"""
URL configuration for frete_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, include


def health(_request):
    return HttpResponse("ok")


def home(request):
    return render(request, "home/index.html")


# Temporary dashboard views (mantendo para compatibilidade)
def dashboard(request):
    return HttpResponse("Dashboard Geral - Em desenvolvimento")


def dashboard_motorista(request):
    from django.shortcuts import redirect

    return redirect("motoristas:dashboard")


def dashboard_gerente(request):
    return HttpResponse("Dashboard Gerente - Em desenvolvimento")


def dashboard_owner(request):
    from django.shortcuts import redirect

    return redirect("gestao:dashboard_dono")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("contas/", include("apps.contas.urls")),
    path("pedidos/", include("apps.pedidos.urls")),
    path("gestao/", include("apps.gestao.urls")),
    path("veiculos/", include("apps.veiculos.urls")),
    path("motoristas/", include("apps.motoristas.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("rotas/", include("apps.rotas.urls")),
    # Include core URLs (including documentation)
    path("", include("core.urls")),
    # Temporary dashboard URLs (mantendo para compatibilidade)
    path("dashboard-old/", dashboard, name="dashboard"),
    path("dashboard/motorista/", dashboard_motorista, name="dashboard_motorista"),
    path("dashboard/gerente/", dashboard_gerente, name="dashboard_gerente"),
    path("dashboard/owner/", dashboard_owner, name="dashboard_owner"),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
