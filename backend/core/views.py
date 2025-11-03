import inspect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import get_resolver
from django.contrib.auth.decorators import user_passes_test
from django.apps import apps
from django.views.decorators.http import require_http_methods


def is_staff_or_superuser(user):
    """Verifica se o usuário é staff ou superuser"""
    return user.is_staff or user.is_superuser


def home(request):
    """
    View da página inicial (home)
    """
    context = {
        "page_title": "Início",
    }
    return render(request, "home/index.html", context)


def sobre(request):
    """
    View da página Saiba Mais / Sobre
    """
    context = {
        "page_title": "Sobre - NeoCargo",
    }
    return render(request, "home/sobre.html", context)


@require_http_methods(["GET"])
def health_check(request):
    """
    Endpoint de health check para monitoramento
    """
    return JsonResponse({"status": "ok", "message": "NeoCargo API is running", "version": "1.0.0"})


@user_passes_test(is_staff_or_superuser)
def documentation_view(request):
    """
    View que gera documentação automática das URLs e views do projeto.
    Apenas usuários staff podem acessar.
    """
    resolver = get_resolver()
    docs_data = []

    def extract_url_patterns(patterns, prefix=""):
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                # É um include(), recursivamente busca os padrões
                new_prefix = f"{prefix}{pattern.pattern}" if prefix else str(pattern.pattern)
                extract_url_patterns(pattern.url_patterns, new_prefix)
            else:
                # É uma URL individual
                full_pattern = f"{prefix}{pattern.pattern}" if prefix else str(pattern.pattern)

                # Pega informações da view
                view_info = {
                    "url_pattern": full_pattern,
                    "name": pattern.name,
                    "view_name": "",
                    "docstring": "",
                    "methods": [],
                    "parameters": [],
                }

                # Tenta pegar a view function/class
                try:
                    if hasattr(pattern.callback, "view_class"):
                        # Class-based view
                        view_class = pattern.callback.view_class
                        view_info["view_name"] = f"{view_class.__module__}.{view_class.__name__}"
                        view_info["docstring"] = inspect.getdoc(view_class) or "Sem documentação"

                        # Pega métodos HTTP permitidos
                        if hasattr(view_class, "http_method_names"):
                            view_info["methods"] = [m.upper() for m in view_class.http_method_names if m != "options"]

                    elif hasattr(pattern.callback, "__name__"):
                        # Function-based view
                        view_func = pattern.callback
                        view_info["view_name"] = f"{view_func.__module__}.{view_func.__name__}"
                        view_info["docstring"] = inspect.getdoc(view_func) or "Sem documentação"
                        view_info["methods"] = ["GET", "POST"]  # Padrão para function views

                    # Extrai parâmetros da URL
                    if "<" in str(pattern.pattern):
                        import re

                        params = re.findall(r"<(\w+):(\w+)>", str(pattern.pattern))
                        view_info["parameters"] = [{"name": name, "type": type_} for type_, name in params]

                except Exception:
                    view_info["view_name"] = "Não disponível"
                    view_info["docstring"] = "Erro ao extrair informações"

                docs_data.append(view_info)

    # Extrai todas as URLs
    extract_url_patterns(resolver.url_patterns)

    # Informações dos apps
    apps_info = []
    for app_config in apps.get_app_configs():
        if not app_config.name.startswith("django."):
            apps_info.append(
                {
                    "name": app_config.name,
                    "verbose_name": app_config.verbose_name,
                    "path": app_config.path,
                }
            )

    context = {
        "docs_data": docs_data,
        "apps_info": apps_info,
        "total_urls": len(docs_data),
    }

    return render(request, "docs/documentation.html", context)
