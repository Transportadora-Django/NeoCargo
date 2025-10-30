from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction, models
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.contas.models import Profile, Role
from .models import ConfiguracaoSistema, SolicitacaoMudancaPerfil, StatusSolicitacao
from .forms import SolicitacaoMudancaPerfilForm, AprovarSolicitacaoForm


def user_has_role(user, required_role):
    """Verifica se o usuário tem o role necessário"""
    try:
        return user.profile.role == required_role
    except Profile.DoesNotExist:
        return False


def require_role(role):
    """Decorator para verificar role do usuário"""

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Você precisa estar logado.")
                return redirect("contas:login")

            if not user_has_role(request.user, role):
                messages.error(request, "Você não tem permissão para acessar esta página.")
                return redirect("home")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


@login_required
def dashboard_dono(request):
    """Dashboard principal do dono com estatísticas e gestão"""
    if not user_has_role(request.user, Role.OWNER):
        messages.error(request, "Acesso negado. Apenas donos podem acessar esta área.")
        return redirect("home")

    # Estatísticas gerais
    total_usuarios = User.objects.count()
    total_clientes = Profile.objects.filter(role=Role.CLIENTE).count()
    total_motoristas = Profile.objects.filter(role=Role.MOTORISTA).count()

    # Total de solicitações pendentes
    total_solicitacoes_pendentes = SolicitacaoMudancaPerfil.objects.filter(status=StatusSolicitacao.PENDENTE).count()

    # Usuários recentes (apenas 5)
    usuarios_recentes = User.objects.select_related("profile").order_by("-date_joined")[:5]

    # Solicitações recentes (apenas 3 para o card)
    solicitacoes_recentes = (
        SolicitacaoMudancaPerfil.objects.filter(status=StatusSolicitacao.PENDENTE)
        .select_related("usuario")
        .order_by("-created_at")[:3]
    )

    # Configuração do sistema
    config = ConfiguracaoSistema.get_config()

    # Estatísticas de veículos e rotas
    from apps.veiculos.models import Veiculo
    from apps.rotas.models import Cidade, Rota
    from apps.pedidos.models import Pedido, StatusPedido

    total_veiculos = Veiculo.objects.count()
    total_cidades = Cidade.objects.filter(ativa=True).count()
    total_rotas = Rota.objects.filter(ativa=True).count()

    # Estatísticas de pedidos
    total_pedidos = Pedido.objects.count()
    pedidos_cotacao = Pedido.objects.filter(status=StatusPedido.COTACAO).count()
    pedidos_pendentes = Pedido.objects.filter(status=StatusPedido.PENDENTE).count()
    pedidos_aprovados = Pedido.objects.filter(status=StatusPedido.APROVADO).count()
    pedidos_em_transporte = Pedido.objects.filter(status=StatusPedido.EM_TRANSPORTE).count()
    pedidos_concluidos = Pedido.objects.filter(status=StatusPedido.CONCLUIDO).count()
    pedidos_cancelados = Pedido.objects.filter(status=StatusPedido.CANCELADO).count()

    # Pedidos recentes
    pedidos_recentes = Pedido.objects.select_related("cliente").order_by("-created_at")[:5]

    context = {
        "titulo": "Dashboard do Dono",
        "total_usuarios": total_usuarios,
        "total_clientes": total_clientes,
        "total_motoristas": total_motoristas,
        "total_solicitacoes_pendentes": total_solicitacoes_pendentes,
        "total_veiculos": total_veiculos,
        "total_cidades": total_cidades,
        "total_rotas": total_rotas,
        "total_pedidos": total_pedidos,
        "pedidos_cotacao": pedidos_cotacao,
        "pedidos_pendentes": pedidos_pendentes,
        "pedidos_aprovados": pedidos_aprovados,
        "pedidos_em_transporte": pedidos_em_transporte,
        "pedidos_concluidos": pedidos_concluidos,
        "pedidos_cancelados": pedidos_cancelados,
        "usuarios_recentes": usuarios_recentes,
        "solicitacoes_recentes": solicitacoes_recentes,
        "pedidos_recentes": pedidos_recentes,
        "config": config,
    }

    return render(request, "gestao/dashboard_dono.html", context)


@login_required
def listar_usuarios(request):
    """Lista todos os usuários com filtros"""
    if not user_has_role(request.user, Role.OWNER):
        messages.error(request, "Acesso negado.")
        return redirect("home")

    usuarios = User.objects.select_related("profile").order_by("-date_joined")

    # Filtros
    role_filter = request.GET.get("role")
    search = request.GET.get("search")

    if role_filter:
        usuarios = usuarios.filter(profile__role=role_filter)

    if search:
        usuarios = usuarios.filter(
            models.Q(username__icontains=search)
            | models.Q(first_name__icontains=search)
            | models.Q(last_name__icontains=search)
            | models.Q(email__icontains=search)
        )

    # Paginação
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "titulo": "Gestão de Usuários",
        "page_obj": page_obj,
        "roles": Role.choices,
        "role_filter": role_filter,
        "search": search,
    }

    return render(request, "gestao/listar_usuarios.html", context)


@login_required
def solicitar_mudanca_perfil(request):
    """Formulário para solicitar mudança de perfil"""
    # Verificar se as solicitações estão abertas
    config = ConfiguracaoSistema.get_config()

    if not config.solicitacoes_abertas:
        messages.warning(request, config.mensagem_solicitacoes_fechadas)
        return redirect("gestao:minhas_solicitacoes")

    # Verifica se já tem uma solicitação pendente
    solicitacao_pendente = SolicitacaoMudancaPerfil.objects.filter(
        usuario=request.user, status=StatusSolicitacao.PENDENTE
    ).exists()

    if solicitacao_pendente:
        messages.warning(request, "Você já possui uma solicitação pendente.")
        return redirect("gestao:minhas_solicitacoes")

    if request.method == "POST":
        form = SolicitacaoMudancaPerfilForm(request.POST, user=request.user)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.usuario = request.user
            solicitacao.status = StatusSolicitacao.PENDENTE
            solicitacao.save()

            messages.success(request, "Solicitação enviada com sucesso! Aguarde a análise do administrador.")
            return redirect("gestao:minhas_solicitacoes")
    else:
        form = SolicitacaoMudancaPerfilForm(user=request.user)

    return render(request, "gestao/solicitar_mudanca.html", {"form": form, "config": config})


@login_required
def minhas_solicitacoes(request):
    """Lista as solicitações do usuário logado"""
    solicitacoes = SolicitacaoMudancaPerfil.objects.filter(usuario=request.user).order_by("-created_at")

    config = ConfiguracaoSistema.get_config()

    context = {
        "titulo": "Minhas Solicitações",
        "solicitacoes": solicitacoes,
        "config": config,
    }

    return render(request, "gestao/minhas_solicitacoes.html", context)


@login_required
def listar_solicitacoes(request):
    """Lista todas as solicitações para aprovação (apenas dono)"""
    if not user_has_role(request.user, Role.OWNER):
        messages.error(request, "Acesso negado.")
        return redirect("home")

    solicitacoes = SolicitacaoMudancaPerfil.objects.select_related("usuario").order_by("-created_at")

    # Filtros
    status_filter = request.GET.get("status")
    if status_filter:
        solicitacoes = solicitacoes.filter(status=status_filter)

    # Paginação
    paginator = Paginator(solicitacoes, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "titulo": "Solicitações de Mudança de Perfil",
        "page_obj": page_obj,
        "status_choices": StatusSolicitacao.choices,
        "status_filter": status_filter,
    }

    return render(request, "gestao/listar_solicitacoes.html", context)


@login_required
def aprovar_solicitacao(request, solicitacao_id):
    """Aprova ou rejeita uma solicitação"""
    if not user_has_role(request.user, Role.OWNER):
        messages.error(request, "Acesso negado.")
        return redirect("home")

    solicitacao = get_object_or_404(SolicitacaoMudancaPerfil, id=solicitacao_id)

    if request.method == "POST":
        form = AprovarSolicitacaoForm(request.POST, instance=solicitacao)
        if form.is_valid():
            with transaction.atomic():
                solicitacao = form.save(commit=False)
                solicitacao.aprovado_por = request.user
                solicitacao.data_aprovacao = timezone.now()
                solicitacao.save()

                # Se aprovada, atualiza o perfil do usuário
                if solicitacao.status == StatusSolicitacao.APROVADA:
                    _aplicar_mudanca_perfil(solicitacao)
                    messages.success(
                        request,
                        f"Solicitação aprovada! {solicitacao.usuario.username} "
                        f"agora é {solicitacao.get_role_solicitada_display()}.",
                    )
                else:
                    messages.info(request, "Solicitação rejeitada.")

                return redirect("gestao:listar_solicitacoes")
    else:
        form = AprovarSolicitacaoForm(instance=solicitacao)

    context = {
        "titulo": "Aprovar Solicitação",
        "solicitacao": solicitacao,
        "form": form,
    }

    return render(request, "gestao/aprovar_solicitacao.html", context)


def _aplicar_mudanca_perfil(solicitacao):
    """Aplica a mudança de perfil aprovada"""
    usuario = solicitacao.usuario

    # Cria ou atualiza o perfil
    perfil, created = Profile.objects.get_or_create(user=usuario, defaults={"role": solicitacao.role_solicitada})

    if not created:
        perfil.role = solicitacao.role_solicitada

    perfil.save()

    # Nota: Veículos serão gerenciados separadamente pelo gerente/dono
    # não são mais vinculados ao cadastro do motorista


@login_required
@require_http_methods(["POST"])
def toggle_solicitacoes(request):
    """Alterna o status de aceitar/pausar solicitações"""
    if not user_has_role(request.user, Role.OWNER):
        messages.error(request, "Acesso negado.")
        return redirect("gestao:dashboard_dono")

    config = ConfiguracaoSistema.get_config()
    config.solicitacoes_abertas = not config.solicitacoes_abertas
    config.atualizado_por = request.user
    config.save()

    status_text = "abertas" if config.solicitacoes_abertas else "pausadas"
    messages.success(request, f"Solicitações {status_text} com sucesso!")

    return redirect("gestao:dashboard_dono")
