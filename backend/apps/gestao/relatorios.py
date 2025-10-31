"""
Módulo de geração de relatórios para Dono e Gerente
"""

from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.pedidos.models import Pedido, StatusPedido
from apps.veiculos.models import Veiculo
from apps.motoristas.models import Motorista, ProblemaEntrega, StatusProblema


class RelatorioGerencial:
    """Classe para gerar dados de relatórios gerenciais"""

    @staticmethod
    def get_periodo_datas(periodo):
        """Retorna data_inicio e data_fim baseado no período selecionado"""
        hoje = timezone.now()

        if periodo == "7dias":
            data_inicio = hoje - timedelta(days=7)
        elif periodo == "30dias":
            data_inicio = hoje - timedelta(days=30)
        elif periodo == "90dias":
            data_inicio = hoje - timedelta(days=90)
        elif periodo == "ano":
            data_inicio = hoje - timedelta(days=365)
        else:  # todos
            data_inicio = None

        return data_inicio, hoje

    @staticmethod
    def get_resumo_financeiro(periodo="30dias"):
        """Retorna resumo financeiro dos pedidos"""
        data_inicio, data_fim = RelatorioGerencial.get_periodo_datas(periodo)

        # Filtrar pedidos concluídos no período
        pedidos = Pedido.objects.filter(status=StatusPedido.CONCLUIDO)
        if data_inicio:
            pedidos = pedidos.filter(updated_at__gte=data_inicio, updated_at__lte=data_fim)

        # Calcular totais
        total_receita = pedidos.aggregate(total=Sum("preco_final"))["total"] or Decimal("0.00")

        total_pedidos = pedidos.count()

        # Ticket médio
        ticket_medio = total_receita / total_pedidos if total_pedidos > 0 else Decimal("0.00")

        # Estimar custos de combustível
        custo_combustivel = RelatorioGerencial.estimar_custo_combustivel(pedidos)

        # Calcular lucro estimado (receita - custo combustível)
        lucro_estimado = total_receita - custo_combustivel

        return {
            "total_receita": total_receita,
            "total_pedidos": total_pedidos,
            "ticket_medio": ticket_medio,
            "custo_combustivel": custo_combustivel,
            "lucro_estimado": lucro_estimado,
            "margem_lucro": round((lucro_estimado / total_receita * 100) if total_receita > 0 else 0, 1),
        }

    @staticmethod
    def estimar_custo_combustivel(pedidos_queryset):
        """
        Estima o custo de combustível para pedidos concluídos
        Usa uma estimativa baseada em 20% do valor do frete
        """
        custo_total = Decimal("0.00")

        for pedido in pedidos_queryset:
            if pedido.preco_final:
                # Estimativa: custo operacional é aproximadamente 30-40% do valor do frete
                # Sendo combustível cerca de 60% dos custos operacionais
                # Portanto: combustível ≈ 18-24% do frete (usaremos 20%)
                custo_estimado = pedido.preco_final * Decimal("0.20")
                custo_total += custo_estimado

        return custo_total

    @staticmethod
    def get_estatisticas_pedidos(periodo="30dias"):
        """Retorna estatísticas de pedidos por status"""
        data_inicio, data_fim = RelatorioGerencial.get_periodo_datas(periodo)

        pedidos = Pedido.objects.all()
        if data_inicio:
            pedidos = pedidos.filter(created_at__gte=data_inicio, created_at__lte=data_fim)

        # Contagem por status
        stats_por_status = pedidos.values("status").annotate(total=Count("id")).order_by("-total")

        # Total geral
        total_geral = pedidos.count()

        # Calcular percentuais
        stats_formatadas = []
        for stat in stats_por_status:
            percentual = (stat["total"] / total_geral * 100) if total_geral > 0 else 0
            stats_formatadas.append(
                {
                    "status": stat["status"],
                    "status_display": dict(StatusPedido.choices).get(stat["status"]),
                    "total": stat["total"],
                    "percentual": round(percentual, 1),
                }
            )

        return {
            "total_geral": total_geral,
            "por_status": stats_formatadas,
            "total_concluidos": pedidos.filter(status=StatusPedido.CONCLUIDO).count(),
            "total_em_transporte": pedidos.filter(status=StatusPedido.EM_TRANSPORTE).count(),
            "total_pendentes": pedidos.filter(status=StatusPedido.PENDENTE).count(),
            "total_cancelados": pedidos.filter(status=StatusPedido.CANCELADO).count(),
        }

    @staticmethod
    def get_estatisticas_veiculos():
        """Retorna estatísticas sobre a frota de veículos"""
        total_veiculos = Veiculo.objects.count()
        veiculos_ativos = Veiculo.objects.filter(ativo=True).count()
        veiculos_inativos = total_veiculos - veiculos_ativos

        # Veículos por tipo
        veiculos_por_tipo = (
            Veiculo.objects.values(tipo=F("especificacao__tipo")).annotate(total=Count("id")).order_by("-total")
        )

        return {
            "total_veiculos": total_veiculos,
            "veiculos_ativos": veiculos_ativos,
            "veiculos_inativos": veiculos_inativos,
            "por_tipo": list(veiculos_por_tipo),
            "taxa_utilizacao": round((veiculos_ativos / total_veiculos * 100) if total_veiculos > 0 else 0, 1),
        }

    @staticmethod
    def get_estatisticas_motoristas():
        """Retorna estatísticas sobre motoristas"""
        total_motoristas = Motorista.objects.count()
        motoristas_ativos = Motorista.objects.filter(profile__user__is_active=True).count()

        return {
            "total_motoristas": total_motoristas,
            "motoristas_ativos": motoristas_ativos,
            "motoristas_inativos": total_motoristas - motoristas_ativos,
        }

    @staticmethod
    def get_estatisticas_problemas(periodo="30dias"):
        """Retorna estatísticas sobre problemas reportados"""
        data_inicio, data_fim = RelatorioGerencial.get_periodo_datas(periodo)

        problemas = ProblemaEntrega.objects.all()
        if data_inicio:
            problemas = problemas.filter(criado_em__gte=data_inicio, criado_em__lte=data_fim)

        total_problemas = problemas.count()

        # Por status
        problemas_pendentes = problemas.filter(status=StatusProblema.PENDENTE).count()
        problemas_em_analise = problemas.filter(status=StatusProblema.EM_ANALISE).count()
        problemas_resolvidos = problemas.filter(status=StatusProblema.RESOLVIDO).count()

        # Por tipo
        problemas_por_tipo = problemas.values("tipo").annotate(total=Count("id")).order_by("-total")

        return {
            "total_problemas": total_problemas,
            "pendentes": problemas_pendentes,
            "em_analise": problemas_em_analise,
            "resolvidos": problemas_resolvidos,
            "por_tipo": list(problemas_por_tipo),
            "taxa_resolucao": round((problemas_resolvidos / total_problemas * 100) if total_problemas > 0 else 0, 1),
        }

    @staticmethod
    def get_pedidos_por_mes(ano=None):
        """Retorna quantidade de pedidos por mês"""
        if ano is None:
            ano = timezone.now().year

        # Inicializar todos os meses com 0
        meses = {i: 0 for i in range(1, 13)}

        # Buscar pedidos do ano
        pedidos = Pedido.objects.filter(created_at__year=ano).values("created_at__month").annotate(total=Count("id"))

        # Preencher com os dados reais
        for pedido in pedidos:
            mes = pedido["created_at__month"]
            meses[mes] = pedido["total"]

        # Converter para lista ordenada
        return [meses[i] for i in range(1, 13)]

    @staticmethod
    def get_receita_por_mes(ano=None):
        """Retorna receita por mês"""
        if ano is None:
            ano = timezone.now().year

        # Inicializar todos os meses com 0
        meses = {i: Decimal("0.00") for i in range(1, 13)}

        # Buscar receita de pedidos concluídos do ano
        receitas = (
            Pedido.objects.filter(updated_at__year=ano, status=StatusPedido.CONCLUIDO)
            .values("updated_at__month")
            .annotate(total=Sum("preco_final"))
        )

        # Preencher com os dados reais
        for receita in receitas:
            mes = receita["updated_at__month"]
            meses[mes] = receita["total"] or Decimal("0.00")

        # Converter para lista ordenada
        return [float(meses[i]) for i in range(1, 13)]

    @staticmethod
    def get_relatorio_completo(periodo="30dias", ano=None):
        """Gera relatório completo com todos os dados"""
        from django.utils import timezone

        if ano is None:
            ano = timezone.now().year

        # Verificar se há dados suficientes
        financeiro = RelatorioGerencial.get_resumo_financeiro(periodo)
        pedidos_mes = RelatorioGerencial.get_pedidos_por_mes(ano)
        receita_mes = RelatorioGerencial.get_receita_por_mes(ano)

        # Verificar se há dados no ano selecionado
        tem_dados_ano = any(pedidos_mes) or any(receita_mes)

        return {
            "financeiro": financeiro,
            "pedidos": RelatorioGerencial.get_estatisticas_pedidos(periodo),
            "veiculos": RelatorioGerencial.get_estatisticas_veiculos(),
            "motoristas": RelatorioGerencial.get_estatisticas_motoristas(),
            "problemas": RelatorioGerencial.get_estatisticas_problemas(periodo),
            "pedidos_por_mes": pedidos_mes,
            "receita_por_mes": receita_mes,
            "tem_dados_ano": tem_dados_ano,
            "tem_dados_financeiros": financeiro["total_pedidos"] > 0,
        }
