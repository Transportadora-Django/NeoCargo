"""Views para motoristas."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.contas.models import Role
from .models import Motorista, AtribuicaoPedido, ProblemaEntrega, StatusAtribuicao, StatusProblema


def require_motorista(view_func):
    """Decorator para verificar se usuário é motorista."""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Você precisa estar logado.")
            return redirect("contas:login")

        try:
            if request.user.profile.role != Role.MOTORISTA:
                messages.error(request, "Acesso restrito a motoristas.")
                return redirect("home")
        except Exception:
            messages.error(request, "Perfil não encontrado.")
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@require_motorista
def dashboard_motorista(request):
    """Dashboard principal do motorista."""
    try:
        motorista = request.user.profile.motorista
    except Motorista.DoesNotExist:
        messages.error(request, "Registro de motorista não encontrado.")
        return redirect("home")

    # Entrega atual (em andamento)
    entrega_atual = (
        AtribuicaoPedido.objects.filter(motorista=motorista, status=StatusAtribuicao.EM_ANDAMENTO)
        .select_related("pedido__cliente", "veiculo__especificacao")
        .first()
    )

    # Próximas entregas (pendentes)
    proximas_entregas = AtribuicaoPedido.objects.filter(
        motorista=motorista, status=StatusAtribuicao.PENDENTE
    ).select_related("pedido__cliente", "veiculo__especificacao")[:3]

    # Histórico recente (últimas 5 entregas concluídas)
    historico_recente = (
        AtribuicaoPedido.objects.filter(motorista=motorista, status=StatusAtribuicao.CONCLUIDO)
        .select_related("pedido__cliente", "veiculo")
        .order_by("-updated_at")[:5]
    )

    # Problemas reportados recentemente
    problemas_recentes = (
        ProblemaEntrega.objects.filter(atribuicao__motorista=motorista)
        .exclude(status=StatusProblema.RESOLVIDO)
        .select_related("atribuicao__pedido")
        .order_by("-criado_em")[:5]
    )

    # Estatísticas
    total_entregas = motorista.entregas_concluidas
    entregas_pendentes = AtribuicaoPedido.objects.filter(
        motorista=motorista, status__in=[StatusAtribuicao.PENDENTE, StatusAtribuicao.EM_ANDAMENTO]
    ).count()
    problemas_abertos = ProblemaEntrega.objects.filter(
        atribuicao__motorista=motorista, status__in=[StatusProblema.PENDENTE, StatusProblema.EM_ANALISE]
    ).count()

    context = {
        "titulo": "Dashboard do Motorista",
        "motorista": motorista,
        "entrega_atual": entrega_atual,
        "proximas_entregas": proximas_entregas,
        "historico_recente": historico_recente,
        "problemas_recentes": problemas_recentes,
        "total_entregas": total_entregas,
        "entregas_pendentes": entregas_pendentes,
        "problemas_abertos": problemas_abertos,
    }

    return render(request, "motoristas/dashboard_motorista.html", context)


@login_required
@require_motorista
def relatar_problema(request, atribuicao_id):
    """Permite motorista relatar problema em uma entrega."""
    try:
        motorista = request.user.profile.motorista
    except Motorista.DoesNotExist:
        messages.error(request, "Registro de motorista não encontrado.")
        return redirect("home")

    # Buscar atribuição e verificar se pertence ao motorista
    atribuicao = get_object_or_404(
        AtribuicaoPedido.objects.select_related("pedido", "veiculo"), id=atribuicao_id, motorista=motorista
    )

    # Verificar se atribuição está em andamento
    if atribuicao.status not in [StatusAtribuicao.PENDENTE, StatusAtribuicao.EM_ANDAMENTO]:
        messages.error(request, "Não é possível relatar problema em entregas concluídas ou canceladas.")
        return redirect("motoristas:dashboard")

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        descricao = request.POST.get("descricao", "").strip()

        if not tipo or not descricao:
            messages.error(request, "Tipo e descrição são obrigatórios.")
            return redirect("motoristas:dashboard")

        # Criar problema
        ProblemaEntrega.objects.create(atribuicao=atribuicao, tipo=tipo, descricao=descricao)

        messages.success(request, "Problema reportado com sucesso. A gestão será notificada.")
        return redirect("motoristas:dashboard")

    # GET - não deveria chegar aqui, redirecionar para dashboard
    return redirect("motoristas:dashboard")


@login_required
@require_motorista
def meus_problemas(request):
    """Lista problemas reportados pelo motorista."""
    try:
        motorista = request.user.profile.motorista
    except Motorista.DoesNotExist:
        messages.error(request, "Registro de motorista não encontrado.")
        return redirect("home")

    # Filtros
    status_filter = request.GET.get("status", "")

    # Query base
    problemas = ProblemaEntrega.objects.filter(atribuicao__motorista=motorista).select_related(
        "atribuicao__pedido", "atribuicao__veiculo"
    )

    # Aplicar filtros
    if status_filter:
        problemas = problemas.filter(status=status_filter)

    # Ordenar por mais recentes
    problemas = problemas.order_by("-criado_em")

    # Paginação
    paginator = Paginator(problemas, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "titulo": "Meus Problemas Reportados",
        "page_obj": page_obj,
        "status_filter": status_filter,
    }

    return render(request, "motoristas/meus_problemas.html", context)


@login_required
@require_motorista
def historico_entregas(request):
    """Lista histórico completo de entregas do motorista."""
    try:
        motorista = request.user.profile.motorista
    except Motorista.DoesNotExist:
        messages.error(request, "Registro de motorista não encontrado.")
        return redirect("home")

    # Filtros
    status_filter = request.GET.get("status", "")
    busca = request.GET.get("q", "").strip()

    # Query base
    entregas = AtribuicaoPedido.objects.filter(motorista=motorista).select_related(
        "pedido__cliente", "veiculo__especificacao"
    )

    # Aplicar filtros
    if status_filter:
        entregas = entregas.filter(status=status_filter)

    if busca:
        entregas = entregas.filter(
            Q(pedido__id__icontains=busca)
            | Q(pedido__cidade_origem__icontains=busca)
            | Q(pedido__cidade_destino__icontains=busca)
        )

    # Ordenar por mais recentes
    entregas = entregas.order_by("-created_at")

    # Estatísticas
    stats = {
        "concluidas": AtribuicaoPedido.objects.filter(motorista=motorista, status=StatusAtribuicao.CONCLUIDO).count(),
        "em_andamento": AtribuicaoPedido.objects.filter(
            motorista=motorista, status=StatusAtribuicao.EM_ANDAMENTO
        ).count(),
        "pendentes": AtribuicaoPedido.objects.filter(motorista=motorista, status=StatusAtribuicao.PENDENTE).count(),
        "canceladas": AtribuicaoPedido.objects.filter(motorista=motorista, status=StatusAtribuicao.CANCELADO).count(),
    }

    # Paginação
    paginator = Paginator(entregas, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "titulo": "Histórico de Entregas",
        "page_obj": page_obj,
        "entregas": page_obj.object_list,
        "stats": stats,
        "status_filter": status_filter,
        "busca": busca,
    }

    return render(request, "motoristas/historico_entregas.html", context)


@login_required
@require_motorista
def iniciar_entrega(request, atribuicao_id):
    """Inicia uma entrega pendente (muda status de PENDENTE para EM_ANDAMENTO)."""
    try:
        motorista = request.user.profile.motorista
    except Motorista.DoesNotExist:
        messages.error(request, "Registro de motorista não encontrado.")
        return redirect("home")

    if request.method != "POST":
        messages.error(request, "Método não permitido.")
        return redirect("motoristas:dashboard")

    # Buscar atribuição e verificar se pertence ao motorista
    atribuicao = get_object_or_404(AtribuicaoPedido, id=atribuicao_id, motorista=motorista)

    # Verificar se está pendente
    if atribuicao.status != StatusAtribuicao.PENDENTE:
        messages.error(request, "Esta entrega não está pendente.")
        return redirect("motoristas:dashboard")

    # Verificar se já tem outra entrega em andamento
    em_andamento = AtribuicaoPedido.objects.filter(motorista=motorista, status=StatusAtribuicao.EM_ANDAMENTO).exists()

    if em_andamento:
        messages.error(
            request,
            "Você já possui uma entrega em andamento. " "Conclua ou reporte problema antes de iniciar outra.",
        )
        return redirect("motoristas:dashboard")

    try:
        # Mudar status para EM_ANDAMENTO
        atribuicao.status = StatusAtribuicao.EM_ANDAMENTO
        atribuicao.save()
        messages.success(request, f"Entrega do Pedido #{atribuicao.pedido.id} iniciada com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao iniciar entrega: {str(e)}")

    return redirect("motoristas:dashboard")


@login_required
@require_motorista
def concluir_entrega(request, atribuicao_id):
    """Marca uma entrega como concluída."""
    try:
        motorista = request.user.profile.motorista
    except Motorista.DoesNotExist:
        messages.error(request, "Registro de motorista não encontrado.")
        return redirect("home")

    if request.method != "POST":
        messages.error(request, "Método não permitido.")
        return redirect("motoristas:dashboard")

    # Buscar atribuição e verificar se pertence ao motorista
    atribuicao = get_object_or_404(AtribuicaoPedido, id=atribuicao_id, motorista=motorista)

    # Verificar se está em andamento
    if atribuicao.status != StatusAtribuicao.EM_ANDAMENTO:
        messages.error(request, "Esta entrega não está em andamento.")
        return redirect("motoristas:dashboard")

    try:
        # Usar o service para concluir entrega
        from .services import AtribuicaoService

        AtribuicaoService.concluir_entrega(atribuicao)
        messages.success(request, "Entrega concluída com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao concluir entrega: {str(e)}")

    return redirect("motoristas:dashboard")
