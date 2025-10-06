from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.pedidos.models import Pedido, StatusPedido
from apps.contas.models import Profile
from .models import SolicitacaoMudancaPerfil


@login_required
def dashboard_cliente(request):
    """
    Dashboard principal do cliente com resumo de pedidos e ações rápidas.
    """
    # Buscar dados do usuário
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Criar perfil se não existir
        profile = Profile.objects.create(user=request.user)

    # Buscar pedidos do cliente - apenas o último
    pedidos_recentes = Pedido.objects.filter(cliente=request.user).order_by("-created_at")[:1]

    # Estatísticas dos pedidos
    total_pedidos = Pedido.objects.filter(cliente=request.user).count()
    pedidos_pendentes = Pedido.objects.filter(
        cliente=request.user, status__in=[StatusPedido.COTACAO, StatusPedido.PENDENTE]
    ).count()
    pedidos_concluidos = Pedido.objects.filter(cliente=request.user, status=StatusPedido.CONCLUIDO).count()

    # Verificar se há solicitação de mudança de perfil pendente
    solicitacao_pendente = SolicitacaoMudancaPerfil.objects.filter(user=request.user, status="pendente").first()

    context = {
        "profile": profile,
        "pedidos_recentes": pedidos_recentes,
        "total_pedidos": total_pedidos,
        "pedidos_pendentes": pedidos_pendentes,
        "pedidos_concluidos": pedidos_concluidos,
        "solicitacao_pendente": solicitacao_pendente,
    }

    return render(request, "dashboard/cliente.html", context)


@login_required
def solicitar_mudanca_perfil(request):
    """
    View para solicitar mudança de perfil.
    """
    if request.method == "POST":
        perfil_solicitado = request.POST.get("perfil_solicitado")
        justificativa = request.POST.get("justificativa")

        if not perfil_solicitado or not justificativa:
            messages.error(request, "Todos os campos são obrigatórios.")
            return redirect("dashboard:cliente")

        # Verificar se já existe uma solicitação pendente
        solicitacao_existente = SolicitacaoMudancaPerfil.objects.filter(user=request.user, status="pendente").first()

        if solicitacao_existente:
            messages.warning(request, "Você já possui uma solicitação de mudança de perfil pendente.")
            return redirect("dashboard:cliente")

        # Criar nova solicitação
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)

        SolicitacaoMudancaPerfil.objects.create(
            user=request.user,
            perfil_atual=profile.role,
            perfil_solicitado=perfil_solicitado,
            justificativa=justificativa,
        )

        messages.success(request, "Solicitação de mudança de perfil enviada com sucesso!")
        return redirect("dashboard:cliente")

    return redirect("dashboard:cliente")
