from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def home(request):
    """
    View da página inicial (home)
    """
    context = {
        "page_title": "Início",
    }
    return render(request, "home/index.html", context)


@require_http_methods(["GET"])
def health_check(request):
    """
    Endpoint de health check para monitoramento
    """
    return JsonResponse({"status": "ok", "message": "NeoCargo API is running", "version": "1.0.0"})
