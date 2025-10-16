from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.pedidos.models import Pedido, StatusPedido
from apps.contas.models import Profile, Role


@login_required
def dashboard_cliente(request):
    """
    Dashboard principal do cliente com resumo de pedidos e ações rápidas.
    Redireciona owners para o dashboard do dono.
    """
    # Buscar dados do usuário
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Criar perfil se não existir
        profile = Profile.objects.create(user=request.user)

    # Redirecionar owners para o dashboard do dono
    if profile.role == Role.OWNER:
        return redirect("gestao:dashboard_dono")

    # Buscar pedidos do cliente - apenas o último
    pedidos_recentes = Pedido.objects.filter(cliente=request.user).order_by("-created_at")[:1]

    # Estatísticas dos pedidos
    total_pedidos = Pedido.objects.filter(cliente=request.user).count()
    pedidos_pendentes = Pedido.objects.filter(
        cliente=request.user, status__in=[StatusPedido.COTACAO, StatusPedido.PENDENTE]
    ).count()
    pedidos_concluidos = Pedido.objects.filter(cliente=request.user, status=StatusPedido.CONCLUIDO).count()

    context = {
        "profile": profile,
        "pedidos_recentes": pedidos_recentes,
        "total_pedidos": total_pedidos,
        "pedidos_pendentes": pedidos_pendentes,
        "pedidos_concluidos": pedidos_concluidos,
    }

    return render(request, "dashboard/cliente.html", context)
