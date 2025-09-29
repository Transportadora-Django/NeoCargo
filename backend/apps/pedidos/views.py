from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Pedido
from .forms import PedidoForm


@login_required
def pedido_criar(request):
    """Criar novo pedido"""
    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user
            pedido.save()
            messages.success(request, "Pedido criado com sucesso! Aguarde aprovação.")
            return redirect("pedidos:listar")
    else:
        form = PedidoForm()

    return render(request, "pedidos/criar.html", {"form": form})


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
    """Listar pedidos do cliente"""
    pedidos_list = Pedido.objects.filter(cliente=request.user)

    # Paginação
    paginator = Paginator(pedidos_list, 10)  # 10 pedidos por página
    page_number = request.GET.get("page")
    pedidos = paginator.get_page(page_number)

    return render(request, "pedidos/listar.html", {"pedidos": pedidos})
