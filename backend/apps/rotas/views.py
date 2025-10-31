"""
Views para gerenciamento de rotas e cidades.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from apps.contas.models import Profile, Role
from .models import Cidade, Rota, ConfiguracaoPreco
from .forms import CidadeForm, RotaForm, ConfiguracaoPrecoForm


def verificar_permissao_gestao(user):
    """Verifica se usuário tem permissão para gerenciar rotas (owner ou gerente)."""
    try:
        profile = user.profile
        return profile.role in [Role.OWNER, Role.GERENTE]
    except Profile.DoesNotExist:
        return False


# ============================================================
# VIEWS PÚBLICAS (Todos podem acessar)
# ============================================================


def mapa_rotas(request):
    """Mapa interativo com todas as cidades e rotas (público)."""
    cidades = Cidade.objects.filter(ativa=True).order_by("estado", "nome")
    rotas = Rota.objects.filter(ativa=True).select_related("origem", "destino")

    # Verificar se usuário pode gerenciar
    pode_gerenciar = False
    if request.user.is_authenticated:
        pode_gerenciar = verificar_permissao_gestao(request.user)

    # Preparar dados para o mapa
    cidades_json = []
    for cidade in cidades:
        if cidade.latitude and cidade.longitude:
            cidades_json.append(
                {
                    "nome": cidade.nome,
                    "estado": cidade.estado,
                    "nome_completo": cidade.nome_completo,
                    "lat": float(cidade.latitude),
                    "lng": float(cidade.longitude),
                }
            )

    rotas_json = []
    for rota in rotas:
        if rota.origem.latitude and rota.origem.longitude and rota.destino.latitude and rota.destino.longitude:
            rotas_json.append(
                {
                    "origem": {
                        "nome": rota.origem.nome_completo,
                        "lat": float(rota.origem.latitude),
                        "lng": float(rota.origem.longitude),
                    },
                    "destino": {
                        "nome": rota.destino.nome_completo,
                        "lat": float(rota.destino.latitude),
                        "lng": float(rota.destino.longitude),
                    },
                    "distancia": float(rota.distancia_km),
                    "tempo": float(rota.tempo_estimado_horas) if rota.tempo_estimado_horas else None,
                }
            )

    context = {
        "titulo": "Mapa de Rotas",
        "cidades": cidades,
        "cidades_json": cidades_json,
        "rotas_json": rotas_json,
        "total_cidades": cidades.count(),
        "total_rotas": rotas.count(),
        "pode_gerenciar": pode_gerenciar,
    }

    return render(request, "rotas/mapa.html", context)


def listar_cidades_publico(request):
    """Lista pública de cidades atendidas."""
    cidades = Cidade.objects.filter(ativa=True).order_by("estado", "nome")

    # Agrupar por estado
    cidades_por_estado = {}
    for cidade in cidades:
        estado = cidade.get_estado_display()
        if estado not in cidades_por_estado:
            cidades_por_estado[estado] = []
        cidades_por_estado[estado].append(cidade)

    context = {
        "titulo": "Cidades Atendidas",
        "cidades_por_estado": cidades_por_estado,
        "total_cidades": cidades.count(),
    }

    return render(request, "rotas/cidades_publico.html", context)


def listar_rotas_publico(request):
    """Lista pública de rotas disponíveis."""
    rotas = (
        Rota.objects.filter(ativa=True).select_related("origem", "destino").order_by("origem__estado", "origem__nome")
    )

    context = {
        "titulo": "Rotas Disponíveis",
        "rotas": rotas,
        "total_rotas": rotas.count(),
    }

    return render(request, "rotas/rotas_publico.html", context)


# ============================================================
# VIEWS DE GESTÃO (Apenas Owner/Gerente)
# ============================================================


@login_required
def dashboard_rotas(request):
    """Dashboard de gestão de rotas (apenas owner/gerente)."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    # Estatísticas
    total_cidades = Cidade.objects.count()
    cidades_ativas = Cidade.objects.filter(ativa=True).count()
    total_rotas = Rota.objects.count()
    rotas_ativas = Rota.objects.filter(ativa=True).count()

    # Configuração atual
    config = ConfiguracaoPreco.get_atual()

    context = {
        "titulo": "Gestão de Rotas",
        "total_cidades": total_cidades,
        "cidades_ativas": cidades_ativas,
        "total_rotas": total_rotas,
        "rotas_ativas": rotas_ativas,
        "config": config,
    }

    return render(request, "rotas/dashboard.html", context)


@login_required
def listar_cidades(request):
    """Lista de cidades para gestão."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    # Busca
    search = request.GET.get("search", "")
    estado_filter = request.GET.get("estado", "")
    status_filter = request.GET.get("status", "")

    cidades = Cidade.objects.all().order_by("estado", "nome")

    if search:
        cidades = cidades.filter(Q(nome__icontains=search))

    if estado_filter:
        cidades = cidades.filter(estado=estado_filter)

    if status_filter == "ativa":
        cidades = cidades.filter(ativa=True)
    elif status_filter == "inativa":
        cidades = cidades.filter(ativa=False)

    # Paginação
    paginator = Paginator(cidades, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "titulo": "Gerenciar Cidades",
        "page_obj": page_obj,
        "search": search,
        "estado_filter": estado_filter,
        "status_filter": status_filter,
    }

    return render(request, "rotas/cidades_listar.html", context)


@login_required
def criar_cidade(request):
    """Criar nova cidade."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    if request.method == "POST":
        form = CidadeForm(request.POST)
        if form.is_valid():
            cidade = form.save()
            messages.success(request, f"Cidade {cidade.nome_completo} criada com sucesso!")
            return redirect("rotas:listar_cidades")
    else:
        form = CidadeForm()

    context = {"titulo": "Nova Cidade", "form": form}
    return render(request, "rotas/cidade_form.html", context)


@login_required
def editar_cidade(request, cidade_id):
    """Editar cidade existente."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    cidade = get_object_or_404(Cidade, id=cidade_id)

    if request.method == "POST":
        form = CidadeForm(request.POST, instance=cidade)
        if form.is_valid():
            cidade = form.save()
            messages.success(request, f"Cidade {cidade.nome_completo} atualizada com sucesso!")
            return redirect("rotas:listar_cidades")
    else:
        form = CidadeForm(instance=cidade)

    context = {"titulo": f"Editar {cidade.nome_completo}", "form": form, "cidade": cidade}
    return render(request, "rotas/cidade_form.html", context)


@login_required
def listar_rotas(request):
    """Lista de rotas para gestão."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    # Busca
    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    rotas = Rota.objects.all().select_related("origem", "destino").order_by("origem__nome", "destino__nome")

    if search:
        rotas = rotas.filter(Q(origem__nome__icontains=search) | Q(destino__nome__icontains=search))

    if status_filter == "ativa":
        rotas = rotas.filter(ativa=True)
    elif status_filter == "inativa":
        rotas = rotas.filter(ativa=False)

    # Paginação
    paginator = Paginator(rotas, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "titulo": "Gerenciar Rotas",
        "page_obj": page_obj,
        "search": search,
        "status_filter": status_filter,
    }

    return render(request, "rotas/rotas_listar.html", context)


@login_required
def criar_rota(request):
    """Criar nova rota."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    if request.method == "POST":
        form = RotaForm(request.POST)
        if form.is_valid():
            rota = form.save()
            messages.success(
                request, f"Rota {rota.origem.nome_completo} → {rota.destino.nome_completo} criada com sucesso!"
            )
            return redirect("rotas:listar_rotas")
    else:
        form = RotaForm()

    context = {"titulo": "Nova Rota", "form": form}
    return render(request, "rotas/rota_form.html", context)


@login_required
def editar_rota(request, rota_id):
    """Editar rota existente."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    rota = get_object_or_404(Rota, id=rota_id)

    if request.method == "POST":
        form = RotaForm(request.POST, instance=rota)
        if form.is_valid():
            rota = form.save()
            messages.success(
                request, f"Rota {rota.origem.nome_completo} → {rota.destino.nome_completo} atualizada com sucesso!"
            )
            return redirect("rotas:listar_rotas")
    else:
        form = RotaForm(instance=rota)

    context = {
        "titulo": f"Editar Rota {rota.origem.nome_completo} → {rota.destino.nome_completo}",
        "form": form,
        "rota": rota,
    }
    return render(request, "rotas/rota_form.html", context)


@login_required
def configurar_precos(request):
    """Configurar preços de combustível e margem de lucro."""
    if not verificar_permissao_gestao(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect("dashboard:cliente")

    config = ConfiguracaoPreco.get_atual()

    if request.method == "POST":
        form = ConfiguracaoPrecoForm(request.POST)
        if form.is_valid():
            # Criar nova configuração (histórico)
            ConfiguracaoPreco.objects.create(
                preco_alcool=form.cleaned_data["preco_alcool"],
                preco_gasolina=form.cleaned_data["preco_gasolina"],
                preco_diesel=form.cleaned_data["preco_diesel"],
                margem_lucro=form.cleaned_data["margem_lucro"],
            )
            messages.success(request, "Configuração de preços atualizada com sucesso!")
            return redirect("rotas:dashboard_rotas")
    else:
        form = ConfiguracaoPrecoForm(
            initial={
                "preco_alcool": config.preco_alcool,
                "preco_gasolina": config.preco_gasolina,
                "preco_diesel": config.preco_diesel,
                "margem_lucro": config.margem_lucro,
            }
        )

    context = {"titulo": "Configurar Preços", "form": form, "config": config}
    return render(request, "rotas/configurar_precos.html", context)
