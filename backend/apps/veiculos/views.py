from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.contas.models import Role
from .models import EspecificacaoVeiculo, Veiculo
from .forms import EspecificacaoVeiculoForm, VeiculoForm


def require_owner(view_func):
    """Decorator para verificar se usuário é owner"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Você precisa estar logado.")
            return redirect("contas:login")

        try:
            if request.user.profile.role != Role.OWNER:
                messages.error(request, "Acesso negado. Apenas donos podem acessar esta área.")
                return redirect("home")
        except Exception:
            messages.error(request, "Acesso negado.")
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


# ============= ESPECIFICAÇÕES DE VEÍCULOS =============


@require_owner
def listar_especificacoes(request):
    """Lista todas as especificações de veículos"""
    especificacoes = EspecificacaoVeiculo.objects.all()

    context = {
        "especificacoes": especificacoes,
        "total_especificacoes": especificacoes.count(),
    }

    return render(request, "veiculos/listar_especificacoes.html", context)


@require_owner
def adicionar_especificacao(request):
    """Adiciona uma nova especificação"""
    if request.method == "POST":
        form = EspecificacaoVeiculoForm(request.POST)
        if form.is_valid():
            especificacao = form.save()
            messages.success(request, f"Especificação {especificacao.get_tipo_display()} adicionada com sucesso!")
            return redirect("veiculos:listar_especificacoes")
    else:
        form = EspecificacaoVeiculoForm()

    context = {"form": form, "titulo": "Adicionar Nova Especificação", "acao": "Adicionar"}

    return render(request, "veiculos/form_especificacao.html", context)


@require_owner
def editar_especificacao(request, especificacao_id):
    """Edita uma especificação existente"""
    especificacao = get_object_or_404(EspecificacaoVeiculo, id=especificacao_id)

    if request.method == "POST":
        form = EspecificacaoVeiculoForm(request.POST, instance=especificacao)
        if form.is_valid():
            especificacao = form.save()
            messages.success(request, f"Especificação {especificacao.get_tipo_display()} atualizada com sucesso!")
            return redirect("veiculos:listar_especificacoes")
    else:
        form = EspecificacaoVeiculoForm(instance=especificacao)

    context = {
        "form": form,
        "especificacao": especificacao,
        "titulo": f"Editar {especificacao.get_tipo_display()}",
        "acao": "Salvar Alterações",
    }

    return render(request, "veiculos/form_especificacao.html", context)


@require_owner
def remover_especificacao(request, especificacao_id):
    """Remove uma especificação"""
    especificacao = get_object_or_404(EspecificacaoVeiculo, id=especificacao_id)

    if request.method == "POST":
        tipo = especificacao.get_tipo_display()
        especificacao.delete()
        messages.success(request, f"Especificação {tipo} removida com sucesso!")
        return redirect("veiculos:listar_especificacoes")

    context = {"especificacao": especificacao}

    return render(request, "veiculos/confirmar_remocao_especificacao.html", context)


# ============= VEÍCULOS =============


@require_owner
def listar_veiculos(request):
    """Lista todos os veículos da empresa"""
    veiculos = Veiculo.objects.select_related("especificacao").all()

    context = {
        "veiculos": veiculos,
        "total_veiculos": veiculos.count(),
    }

    return render(request, "veiculos/listar_veiculos.html", context)


@require_owner
def adicionar_veiculo(request):
    """Adiciona um novo veículo"""
    if request.method == "POST":
        form = VeiculoForm(request.POST)
        if form.is_valid():
            veiculo = form.save()
            messages.success(
                request, f"Veículo {veiculo.marca} {veiculo.modelo} ({veiculo.placa}) adicionado com sucesso!"
            )
            return redirect("veiculos:listar_veiculos")
    else:
        form = VeiculoForm()

    context = {"form": form, "titulo": "Adicionar Novo Veículo", "acao": "Adicionar"}

    return render(request, "veiculos/form_veiculo.html", context)


@require_owner
def editar_veiculo(request, veiculo_id):
    """Edita um veículo existente"""
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)

    if request.method == "POST":
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            veiculo = form.save()
            messages.success(request, f"Veículo {veiculo.marca} {veiculo.modelo} atualizado com sucesso!")
            return redirect("veiculos:listar_veiculos")
    else:
        form = VeiculoForm(instance=veiculo)

    context = {
        "form": form,
        "veiculo": veiculo,
        "titulo": f"Editar {veiculo.marca} {veiculo.modelo}",
        "acao": "Salvar Alterações",
    }

    return render(request, "veiculos/form_veiculo.html", context)


@require_owner
def remover_veiculo(request, veiculo_id):
    """Remove um veículo"""
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)

    if request.method == "POST":
        veiculo_info = f"{veiculo.marca} {veiculo.modelo} ({veiculo.placa})"
        veiculo.delete()
        messages.success(request, f"Veículo {veiculo_info} removido com sucesso!")
        return redirect("veiculos:listar_veiculos")

    context = {"veiculo": veiculo}

    return render(request, "veiculos/confirmar_remocao_veiculo.html", context)
