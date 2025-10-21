from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from apps.contas.models import Profile, Role
from .models import Pedido, StatusPedido
from .forms import PedidoForm


@login_required
def pedido_criar(request):
    """Criar novo pedido - bloqueado para owners"""
    # Verificar se é owner
    try:
        if request.user.profile.role == Role.OWNER:
            messages.warning(request, "Owners não podem criar pedidos. Use a área de gestão para gerenciar o sistema.")
            return redirect("gestao:dashboard_dono")
    except Profile.DoesNotExist:
        pass

    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user
            pedido.status = StatusPedido.COTACAO
            pedido.save()
            messages.success(request, "Cotação gerada com sucesso! Escolha a melhor opção para você.")
            return redirect("pedidos:gerar_cotacao", pedido_id=pedido.id)
    else:
        form = PedidoForm()

    return render(request, "pedidos/criar.html", {"form": form})


@login_required
def gerar_cotacao(request, pedido_id):
    """Exibir opções de cotação para o pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    # Verifica se o pedido está em status de cotação
    if pedido.status != StatusPedido.COTACAO:
        messages.warning(request, "Este pedido já foi confirmado.")
        return redirect("pedidos:listar")

    # Opções de cotação (valores placeholder - serão calculados pelo gerente depois)
    opcoes = {
        "economico": {"preco": 837.60, "prazo": "5-7 dias", "veiculo": "Caminhão 3/4"},
        "rapido": {"preco": 1361.10, "prazo": "1-2 dias", "veiculo": "Van Expressa"},
        "custo_beneficio": {"preco": 1047.00, "prazo": "3-4 dias", "veiculo": "Caminhão Toco"},
    }

    context = {"titulo": "Opções de Cotação", "pedido": pedido, "opcoes": opcoes}

    return render(request, "pedidos/cotacao.html", context)


@login_required
def confirmar_pedido(request, pedido_id):
    """Confirmar pedido com a opção escolhida"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if request.method == "POST":
        opcao = request.POST.get("opcao")

        if opcao not in ["economico", "rapido", "custo_beneficio"]:
            messages.error(request, "Opção inválida. Por favor, selecione uma opção válida.")
            return redirect("pedidos:gerar_cotacao", pedido_id=pedido.id)

        # Salva a opção escolhida e muda o status para pendente
        pedido.opcao = opcao
        pedido.status = StatusPedido.PENDENTE
        pedido.save()

        messages.success(request, "Pedido confirmado com sucesso! Nossa equipe entrará em contato em breve.")
        return redirect("pedidos:listar")

    return redirect("pedidos:gerar_cotacao", pedido_id=pedido.id)


@login_required
def cancelar_pedido(request, pedido_id):
    """Cancelar pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if request.method == "POST":
        if pedido.cancelar():
            messages.success(request, "Pedido cancelado com sucesso!")
        else:
            messages.error(request, "Este pedido não pode ser cancelado.")

    return redirect("pedidos:listar")


@login_required
def pedido_listar(request):
    """Listar pedidos - todos para owner, apenas do cliente para outros"""
    try:
        profile = request.user.profile
        # Owner vê todos os pedidos
        if profile.role == Role.OWNER:
            pedidos_list = Pedido.objects.all().select_related("cliente")
        else:
            # Outros usuários veem apenas seus pedidos
            pedidos_list = Pedido.objects.filter(cliente=request.user)
    except Profile.DoesNotExist:
        # Se não tem perfil, vê apenas seus pedidos
        pedidos_list = Pedido.objects.filter(cliente=request.user)

    # Paginação
    paginator = Paginator(pedidos_list, 10)  # 10 pedidos por página
    page_number = request.GET.get("page")
    pedidos = paginator.get_page(page_number)

    return render(request, "pedidos/listar.html", {"pedidos": pedidos})
