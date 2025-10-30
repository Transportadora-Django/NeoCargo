"""
Services para lógica de atribuição automática de motoristas e veículos
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from apps.motoristas.models import Motorista, AtribuicaoPedido, StatusAtribuicao, CategoriaCNH
from apps.pedidos.models import StatusPedido
from apps.veiculos.models import Veiculo
from apps.rotas.models import Cidade


class AtribuicaoService:
    """Service para gerenciar atribuição de motoristas e veículos a pedidos"""

    # Mapeamento de hierarquia de CNH (categoria maior pode dirigir categoria menor)
    HIERARQUIA_CNH = {
        CategoriaCNH.B: [CategoriaCNH.B],
        CategoriaCNH.C: [CategoriaCNH.B, CategoriaCNH.C],
        CategoriaCNH.D: [CategoriaCNH.B, CategoriaCNH.C, CategoriaCNH.D],
        CategoriaCNH.E: [CategoriaCNH.B, CategoriaCNH.C, CategoriaCNH.D, CategoriaCNH.E],
    }

    @classmethod
    def pode_dirigir_veiculo(cls, motorista_cnh, veiculo_cnh_minima):
        """
        Verifica se um motorista com determinada CNH pode dirigir um veículo

        Args:
            motorista_cnh: Categoria CNH do motorista (ex: 'D')
            veiculo_cnh_minima: Categoria CNH mínima do veículo (ex: 'C')

        Returns:
            bool: True se pode dirigir, False caso contrário
        """
        if not veiculo_cnh_minima:
            return True  # Se veículo não tem restrição, qualquer CNH serve

        categorias_permitidas = cls.HIERARQUIA_CNH.get(motorista_cnh, [])
        return veiculo_cnh_minima in categorias_permitidas

    @classmethod
    def buscar_motorista_disponivel(cls, cidade_origem, cnh_minima=None):
        """
        Busca um motorista disponível na cidade de origem

        Args:
            cidade_origem: Cidade onde deve estar o motorista
            cnh_minima: Categoria CNH mínima (opcional)

        Returns:
            Motorista ou None
        """
        query = Motorista.objects.filter(disponivel=True, sede_atual=cidade_origem)

        # Se tem restrição de CNH, filtra por motoristas que podem dirigir
        if cnh_minima:
            categorias_validas = []
            for cat, permitidas in cls.HIERARQUIA_CNH.items():
                if cnh_minima in permitidas:
                    categorias_validas.append(cat)

            query = query.filter(cnh_categoria__in=categorias_validas)

        # Ordena por número de entregas (prioriza quem tem menos entregas)
        return query.order_by("entregas_concluidas").first()

    @classmethod
    def buscar_veiculo_disponivel(cls, cidade_origem, motorista=None):
        """
        Busca um veículo disponível na cidade de origem

        Args:
            cidade_origem: Cidade onde deve estar o veículo
            motorista: Motorista (para verificar compatibilidade de CNH)

        Returns:
            Veiculo ou None
        """
        query = Veiculo.objects.filter(ativo=True, sede_atual=cidade_origem)

        # Exclui veículos que estão em atribuições ativas
        veiculos_ocupados = AtribuicaoPedido.objects.filter(status=StatusAtribuicao.EM_ANDAMENTO).values_list(
            "veiculo_id", flat=True
        )
        query = query.exclude(id__in=veiculos_ocupados)

        # Se tem motorista, filtra por veículos que ele pode dirigir
        if motorista:
            veiculos_compativeis = []
            for veiculo in query:
                if cls.pode_dirigir_veiculo(motorista.cnh_categoria, veiculo.categoria_minima_cnh):
                    veiculos_compativeis.append(veiculo.id)

            query = query.filter(id__in=veiculos_compativeis)

        return query.first()

    @classmethod
    @transaction.atomic
    def atribuir_pedido(cls, pedido):
        """
        Atribui automaticamente motorista e veículo a um pedido aprovado

        Args:
            pedido: Instância de Pedido

        Returns:
            AtribuicaoPedido ou None

        Raises:
            ValidationError: Se não houver motorista ou veículo disponível
        """
        # Verifica se pedido está aprovado
        if pedido.status != StatusPedido.APROVADO:
            raise ValidationError("Pedido precisa estar aprovado para atribuição.")

        # Verifica se já tem atribuição
        if hasattr(pedido, "atribuicao"):
            raise ValidationError("Pedido já possui atribuição.")

        # Busca cidade de origem
        try:
            # Parsear cidade_origem (formato: "Cidade - Estado" ou "Cidade/Estado")
            if " - " in pedido.cidade_origem:
                cidade_nome = pedido.cidade_origem.split(" - ")[0].strip()
            elif "/" in pedido.cidade_origem:
                cidade_nome = pedido.cidade_origem.split("/")[0].strip()
            else:
                cidade_nome = pedido.cidade_origem.strip()

            cidade_origem = Cidade.objects.filter(nome__iexact=cidade_nome, ativa=True).first()

            if not cidade_origem:
                raise ValidationError(f"Cidade de origem '{pedido.cidade_origem}' não encontrada no sistema.")

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Erro ao buscar cidade de origem: {str(e)}")

        # 1. Busca veículo disponível primeiro
        veiculo = cls.buscar_veiculo_disponivel(cidade_origem)

        if not veiculo:
            raise ValidationError(
                f"Não há veículos disponíveis na cidade {cidade_origem.nome_completo} para este pedido."
            )

        # 2. Busca motorista compatível com o veículo
        motorista = cls.buscar_motorista_disponivel(cidade_origem, veiculo.categoria_minima_cnh)

        if not motorista:
            cnh_info = f" com CNH {veiculo.categoria_minima_cnh}" if veiculo.categoria_minima_cnh else ""
            raise ValidationError(f"Não há motoristas disponíveis{cnh_info} na cidade {cidade_origem.nome_completo}.")

        # 3. Cria atribuição
        atribuicao = AtribuicaoPedido.objects.create(
            pedido=pedido, motorista=motorista, veiculo=veiculo, status=StatusAtribuicao.PENDENTE
        )

        # 4. Marca motorista e veículo como indisponíveis
        motorista.disponivel = False
        motorista.save()

        # 5. Atualiza status do pedido
        pedido.status = StatusPedido.EM_TRANSPORTE
        pedido.save()

        return atribuicao

    @classmethod
    @transaction.atomic
    def concluir_entrega(cls, atribuicao):
        """
        Marca uma entrega como concluída e atualiza sedes

        Args:
            atribuicao: Instância de AtribuicaoPedido

        Returns:
            AtribuicaoPedido atualizado
        """
        if atribuicao.status == StatusAtribuicao.CONCLUIDO:
            raise ValidationError("Esta entrega já foi concluída.")

        # Busca cidade de destino
        try:
            # Parsear cidade_destino (formato: "Cidade - Estado" ou "Cidade/Estado")
            if " - " in atribuicao.pedido.cidade_destino:
                cidade_nome = atribuicao.pedido.cidade_destino.split(" - ")[0].strip()
            elif "/" in atribuicao.pedido.cidade_destino:
                cidade_nome = atribuicao.pedido.cidade_destino.split("/")[0].strip()
            else:
                cidade_nome = atribuicao.pedido.cidade_destino.strip()

            cidade_destino = Cidade.objects.filter(nome__iexact=cidade_nome, ativa=True).first()

            if not cidade_destino:
                raise ValidationError(
                    f"Cidade de destino '{atribuicao.pedido.cidade_destino}' não encontrada no sistema."
                )

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Erro ao buscar cidade de destino: {str(e)}")

        # Atualiza status da atribuição
        atribuicao.status = StatusAtribuicao.CONCLUIDO
        atribuicao.save()

        # Atualiza sede do motorista e veículo para cidade de destino
        atribuicao.motorista.sede_atual = cidade_destino
        atribuicao.motorista.disponivel = True  # Volta a ficar disponível
        atribuicao.motorista.entregas_concluidas += 1
        atribuicao.motorista.save()

        atribuicao.veiculo.sede_atual = cidade_destino
        atribuicao.veiculo.save()

        # Atualiza status do pedido
        atribuicao.pedido.status = StatusPedido.CONCLUIDO
        atribuicao.pedido.save()

        return atribuicao

    @classmethod
    @transaction.atomic
    def cancelar_atribuicao(cls, atribuicao, motivo=None):
        """
        Cancela uma atribuição e libera recursos

        Args:
            atribuicao: Instância de AtribuicaoPedido
            motivo: Motivo do cancelamento (opcional)

        Returns:
            AtribuicaoPedido atualizado
        """
        if atribuicao.status == StatusAtribuicao.CONCLUIDO:
            raise ValidationError("Não é possível cancelar uma entrega já concluída.")

        # Libera motorista e veículo
        atribuicao.motorista.disponivel = True
        atribuicao.motorista.save()

        # Atualiza status
        atribuicao.status = StatusAtribuicao.CANCELADO
        if motivo:
            atribuicao.observacoes = motivo
        atribuicao.save()

        # Volta pedido para status aprovado
        atribuicao.pedido.status = StatusPedido.APROVADO
        atribuicao.pedido.save()

        return atribuicao
