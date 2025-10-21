from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from decimal import Decimal
from apps.contas.models import Profile, Role
from apps.rotas.models import Rota, Cidade
from .models import Pedido, StatusPedido, OpcaoCotacao
from .forms import PedidoForm
from .calculadora import CalculadoraCustos


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

    # Buscar rota entre as cidades (formato: "Cidade - Estado")
    if " - " not in pedido.cidade_origem or " - " not in pedido.cidade_destino:
        # Formato antigo - não tem rota cadastrada, usar valores padrão
        messages.warning(
            request,
            "Sistema de rotas não disponível para este pedido. "
            "Entre em contato com o suporte para cotação manual."
        )
        pedido.status = StatusPedido.PENDENTE
        pedido.save()
        return redirect("pedidos:listar")

    try:
        # Parsear nome da cidade (formato: "São Paulo - São Paulo")
        origem_nome, origem_estado_nome = pedido.cidade_origem.rsplit(" - ", 1)
        destino_nome, destino_estado_nome = pedido.cidade_destino.rsplit(" - ", 1)

        # Buscar cidades pelo nome (o estado é apenas para exibição)
        cidade_origem = Cidade.objects.filter(nome=origem_nome.strip(), ativa=True).first()
        cidade_destino = Cidade.objects.filter(nome=destino_nome.strip(), ativa=True).first()

        if not cidade_origem or not cidade_destino:
            raise Cidade.DoesNotExist()

        rota = Rota.objects.get(origem=cidade_origem, destino=cidade_destino, ativa=True)
    except (Cidade.DoesNotExist, Rota.DoesNotExist):
        messages.error(request, "Rota não encontrada. Entre em contato com o suporte.")
        return redirect("pedidos:listar")

    # Calcular cotações usando a calculadora
    calculadora = CalculadoraCustos()

    # Converter prazo de dias para horas (24h por dia)
    tempo_maximo_horas = Decimal(str(pedido.prazo_desejado * 24))

    resultados = calculadora.calcular_para_rota(
        rota=rota,
        peso_carga_kg=pedido.peso_carga,
        tempo_maximo_horas=tempo_maximo_horas
    )

    # Verificar se há veículos disponíveis
    if not resultados["menor_custo"]:
        messages.error(
            request,
            "Nenhum veículo disponível pode atender este pedido. "
            "Verifique o peso da carga ou o prazo desejado."
        )
        pedido.status = StatusPedido.RECUSADO
        pedido.save()
        return redirect("pedidos:listar")

    # Salvar cotações no pedido
    menor_custo = resultados["menor_custo"]
    mais_rapido = resultados["mais_rapido"]
    melhor_cb = resultados["melhor_custo_beneficio"]

    pedido.cotacao_economico_valor = menor_custo.custo_com_margem
    pedido.cotacao_economico_tempo = menor_custo.tempo_viagem_horas
    pedido.cotacao_economico_veiculo = str(menor_custo.veiculo)

    pedido.cotacao_rapido_valor = mais_rapido.custo_com_margem
    pedido.cotacao_rapido_tempo = mais_rapido.tempo_viagem_horas
    pedido.cotacao_rapido_veiculo = str(mais_rapido.veiculo)

    pedido.cotacao_custo_beneficio_valor = melhor_cb.custo_com_margem
    pedido.cotacao_custo_beneficio_tempo = melhor_cb.tempo_viagem_horas
    pedido.cotacao_custo_beneficio_veiculo = str(melhor_cb.veiculo)

    pedido.save()

    # Preparar dados para o template
    def calcular_prazo_total(horas, dias_logistica):
        """Calcula o prazo total: tempo de viagem + dias de logística"""
        import math
        dias_viagem = math.ceil(float(horas) / 24)  # Arredondar para cima
        dias_total = dias_viagem + dias_logistica
        if dias_total == 1:
            return "1 dia"
        else:
            return f"{dias_total} dias"

    # Dias de logística e taxas de agilização por tipo de opção
    DIAS_LOGISTICA_ECONOMICO = 2
    DIAS_LOGISTICA_RAPIDO = 0
    DIAS_LOGISTICA_CUSTO_BENEFICIO = 1

    # Taxas de agilização de logística (percentual sobre o custo base)
    TAXA_AGILIZACAO_ECONOMICO = Decimal("0")      # 0% - sem taxa
    TAXA_AGILIZACAO_RAPIDO = Decimal("0.30")      # 30% - entrega expressa
    TAXA_AGILIZACAO_CUSTO_BENEFICIO = Decimal("0.15")  # 15% - agilização moderada

    # Calcular preços com taxas de agilização
    preco_economico = menor_custo.custo_com_margem * (Decimal("1") + TAXA_AGILIZACAO_ECONOMICO)
    preco_rapido = mais_rapido.custo_com_margem * (Decimal("1") + TAXA_AGILIZACAO_RAPIDO)
    preco_custo_beneficio = melhor_cb.custo_com_margem * (Decimal("1") + TAXA_AGILIZACAO_CUSTO_BENEFICIO)

    opcoes = {
        "economico": {
            "preco": preco_economico,
            "tempo_horas": menor_custo.tempo_viagem_horas,
            "tempo_dias": menor_custo.tempo_viagem_horas / 24,
            "prazo": calcular_prazo_total(menor_custo.tempo_viagem_horas, DIAS_LOGISTICA_ECONOMICO),
            "veiculo": str(menor_custo.veiculo),
            "combustivel": menor_custo.combustivel_usado,
            "detalhes": menor_custo,
        },
        "rapido": {
            "preco": preco_rapido,
            "tempo_horas": mais_rapido.tempo_viagem_horas,
            "tempo_dias": mais_rapido.tempo_viagem_horas / 24,
            "prazo": calcular_prazo_total(mais_rapido.tempo_viagem_horas, DIAS_LOGISTICA_RAPIDO),
            "veiculo": str(mais_rapido.veiculo),
            "combustivel": mais_rapido.combustivel_usado,
            "detalhes": mais_rapido,
        },
        "custo_beneficio": {
            "preco": preco_custo_beneficio,
            "tempo_horas": melhor_cb.tempo_viagem_horas,
            "tempo_dias": melhor_cb.tempo_viagem_horas / 24,
            "prazo": calcular_prazo_total(melhor_cb.tempo_viagem_horas, DIAS_LOGISTICA_CUSTO_BENEFICIO),
            "veiculo": str(melhor_cb.veiculo),
            "combustivel": melhor_cb.combustivel_usado,
            "detalhes": melhor_cb,
        },
    }

    context = {
        "titulo": "Opções de Cotação",
        "pedido": pedido,
        "opcoes": opcoes,
        "rota": rota,
    }

    return render(request, "pedidos/cotacao.html", context)


@login_required
def confirmar_pedido(request, pedido_id):
    """Confirmar pedido com a opção escolhida"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if request.method == "POST":
        opcao = request.POST.get("opcao")

        # Mapear opção para o enum
        opcao_map = {
            "economico": OpcaoCotacao.ECONOMICO,
            "rapido": OpcaoCotacao.RAPIDO,
            "custo_beneficio": OpcaoCotacao.CUSTO_BENEFICIO,
        }

        if opcao not in opcao_map:
            messages.error(request, "Opção inválida. Por favor, selecione uma opção válida.")
            return redirect("pedidos:gerar_cotacao", pedido_id=pedido.id)

        # Salva a opção escolhida e define preço/prazo final baseado na opção
        pedido.opcao = opcao_map[opcao]

        # Definir preço e prazo final baseado na opção escolhida
        if opcao == "economico":
            pedido.preco_final = pedido.cotacao_economico_valor
            pedido.prazo_final = f"{pedido.cotacao_economico_tempo:.1f} horas"
            pedido.veiculo_final = pedido.cotacao_economico_veiculo
        elif opcao == "rapido":
            pedido.preco_final = pedido.cotacao_rapido_valor
            pedido.prazo_final = f"{pedido.cotacao_rapido_tempo:.1f} horas"
            pedido.veiculo_final = pedido.cotacao_rapido_veiculo
        else:  # custo_beneficio
            pedido.preco_final = pedido.cotacao_custo_beneficio_valor
            pedido.prazo_final = f"{pedido.cotacao_custo_beneficio_tempo:.1f} horas"
            pedido.veiculo_final = pedido.cotacao_custo_beneficio_veiculo

        pedido.status = StatusPedido.PENDENTE
        pedido.save()

        messages.success(
            request,
            f"Pedido confirmado com sucesso! Valor: R$ {pedido.preco_final:.2f}. "
            "Nossa equipe entrará em contato em breve."
        )
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


@login_required
def api_destinos_disponiveis(request):
    """API para retornar destinos disponíveis baseado na origem selecionada"""
    from django.http import JsonResponse

    origem = request.GET.get('origem', '')

    if not origem or " - " not in origem:
        return JsonResponse({'destinos': []})

    try:
        # Parsear origem (formato: "Cidade - Estado")
        origem_nome, origem_estado_nome = origem.rsplit(" - ", 1)

        # Buscar cidade de origem
        cidade_origem = Cidade.objects.filter(
            nome=origem_nome.strip(),
            ativa=True
        ).first()

        if not cidade_origem:
            return JsonResponse({'destinos': []})

        # Buscar todas as rotas ativas que partem desta origem
        rotas = Rota.objects.filter(
            origem=cidade_origem,
            ativa=True
        ).select_related('destino')

        # Criar lista de destinos disponíveis
        destinos = []
        for rota in rotas:
            destino_label = f"{rota.destino.nome} - {rota.destino.get_estado_display()}"
            destinos.append(destino_label)

        return JsonResponse({'destinos': destinos})

    except Exception as e:
        return JsonResponse({'destinos': [], 'error': str(e)})
