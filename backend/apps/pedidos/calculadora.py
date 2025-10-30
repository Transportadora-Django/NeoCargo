"""
Calculadora de custos de transporte baseada nas regras do Zé do Caminhão.
"""

from decimal import Decimal
from typing import Dict, Optional
from dataclasses import dataclass
from apps.veiculos.models import Veiculo, TipoCombustivel
from apps.rotas.models import ConfiguracaoPreco, Rota


@dataclass
class ResultadoCalculo:
    """Resultado do cálculo para um veículo específico."""

    veiculo: Veiculo
    combustivel_usado: str
    rendimento_final: Decimal
    litros_necessarios: Decimal
    custo_combustivel: Decimal
    custo_pedagio: Decimal
    custo_total: Decimal
    custo_com_margem: Decimal
    tempo_viagem_horas: Decimal
    pode_transportar: bool
    motivo_recusa: Optional[str] = None


class CalculadoraCustos:
    """Calculadora de custos de transporte."""

    def __init__(self):
        self.config = ConfiguracaoPreco.get_atual()

    def calcular_rendimento_final(
        self, rendimento_base: Decimal, peso_carga_kg: Decimal, reducao_por_kg: Decimal
    ) -> Decimal:
        """
        Calcula o rendimento final considerando a redução por peso.

        Args:
            rendimento_base: Rendimento base do veículo (Km/L)
            peso_carga_kg: Peso da carga em kg
            reducao_por_kg: Redução no rendimento por kg de carga

        Returns:
            Rendimento final em Km/L
        """
        reducao_total = peso_carga_kg * reducao_por_kg
        rendimento_final = rendimento_base - reducao_total
        # Garantir que o rendimento não seja negativo
        return max(Decimal("0.01"), Decimal(str(rendimento_final)))

    def calcular_tempo_viagem(self, distancia_km: Decimal, velocidade_media: int) -> Decimal:
        """
        Calcula o tempo de viagem em horas.

        Args:
            distancia_km: Distância em km
            velocidade_media: Velocidade média em km/h

        Returns:
            Tempo em horas
        """
        return distancia_km / Decimal(str(velocidade_media))

    def calcular_custo_veiculo(
        self,
        veiculo: Veiculo,
        peso_carga_kg: Decimal,
        distancia_km: Decimal,
        tempo_maximo_horas: Optional[Decimal],
        pedagio_valor: Decimal,
        usar_combustivel_alternativo: bool = False,
    ) -> ResultadoCalculo:
        """
        Calcula o custo de transporte para um veículo específico.

        Args:
            veiculo: Instância do veículo
            peso_carga_kg: Peso da carga em kg
            distancia_km: Distância a percorrer em km
            tempo_maximo_horas: Tempo máximo permitido (None = sem limite)
            pedagio_valor: Valor do pedágio na rota
            usar_combustivel_alternativo: Se deve usar combustível alternativo

        Returns:
            ResultadoCalculo com todos os dados calculados
        """
        espec = veiculo.especificacao

        # Verificar se pode transportar o peso
        if peso_carga_kg > espec.carga_maxima:
            return ResultadoCalculo(
                veiculo=veiculo,
                combustivel_usado="",
                rendimento_final=Decimal("0"),
                litros_necessarios=Decimal("0"),
                custo_combustivel=Decimal("0"),
                custo_pedagio=Decimal("0"),
                custo_total=Decimal("0"),
                custo_com_margem=Decimal("0"),
                tempo_viagem_horas=Decimal("0"),
                pode_transportar=False,
                motivo_recusa=f"Carga excede limite de {espec.carga_maxima} kg",
            )

        # Determinar combustível e rendimento
        if usar_combustivel_alternativo and espec.combustivel_alternativo:
            combustivel = espec.combustivel_alternativo
            rendimento_base = Decimal(str(espec.rendimento_alternativo))
            reducao_por_kg = Decimal(str(espec.reducao_rendimento_alternativo))
        else:
            combustivel = espec.combustivel_principal
            rendimento_base = Decimal(str(espec.rendimento_principal))
            reducao_por_kg = Decimal(str(espec.reducao_rendimento_principal))

        # Calcular rendimento final
        rendimento_final = self.calcular_rendimento_final(rendimento_base, peso_carga_kg, reducao_por_kg)

        # Calcular litros necessários
        litros_necessarios = distancia_km / rendimento_final

        # Obter preço do combustível
        if combustivel == TipoCombustivel.DIESEL:
            preco_litro = self.config.preco_diesel
        elif combustivel == TipoCombustivel.GASOLINA:
            preco_litro = self.config.preco_gasolina
        else:  # ALCOOL
            preco_litro = self.config.preco_alcool

        # Calcular custos
        custo_combustivel = litros_necessarios * preco_litro
        custo_total = custo_combustivel + pedagio_valor
        custo_com_margem = custo_total * (Decimal("1") + (self.config.margem_lucro / Decimal("100")))

        # Calcular tempo de viagem
        tempo_viagem = self.calcular_tempo_viagem(distancia_km, espec.velocidade_media)

        # Verificar se atende o prazo
        pode_transportar = True
        motivo_recusa = None

        if tempo_maximo_horas and tempo_viagem > tempo_maximo_horas:
            pode_transportar = False
            motivo_recusa = f"Tempo de viagem ({tempo_viagem:.2f}h) excede limite de {tempo_maximo_horas}h"

        return ResultadoCalculo(
            veiculo=veiculo,
            combustivel_usado=combustivel,
            rendimento_final=rendimento_final,
            litros_necessarios=litros_necessarios,
            custo_combustivel=custo_combustivel,
            custo_pedagio=pedagio_valor,
            custo_total=custo_total,
            custo_com_margem=custo_com_margem,
            tempo_viagem_horas=tempo_viagem,
            pode_transportar=pode_transportar,
            motivo_recusa=motivo_recusa,
        )

    def calcular_melhor_opcao(
        self,
        peso_carga_kg: Decimal,
        distancia_km: Decimal,
        tempo_maximo_horas: Optional[Decimal],
        pedagio_valor: Decimal,
    ) -> Dict[str, Optional[ResultadoCalculo]]:
        """
        Calcula as melhores opções de veículos disponíveis.

        Args:
            peso_carga_kg: Peso da carga em kg
            distancia_km: Distância em km
            tempo_maximo_horas: Tempo máximo em horas (None = sem limite)
            pedagio_valor: Valor do pedágio

        Returns:
            Dicionário com:
            - menor_custo: Veículo mais econômico (menor consumo de combustível)
            - mais_rapido: Veículo mais rápido (maior velocidade)
            - melhor_custo_beneficio: Melhor equilíbrio entre preço e velocidade
            - todos_resultados: Lista com todos os resultados
        """
        veiculos_disponiveis = Veiculo.objects.filter(ativo=True).select_related("especificacao")

        resultados = []

        for veiculo in veiculos_disponiveis:
            # Calcular com combustível principal
            resultado_principal = self.calcular_custo_veiculo(
                veiculo,
                peso_carga_kg,
                distancia_km,
                tempo_maximo_horas,
                pedagio_valor,
                usar_combustivel_alternativo=False,
            )

            # Se tem combustível alternativo, calcular também
            if veiculo.especificacao.combustivel_alternativo:
                resultado_alternativo = self.calcular_custo_veiculo(
                    veiculo,
                    peso_carga_kg,
                    distancia_km,
                    tempo_maximo_horas,
                    pedagio_valor,
                    usar_combustivel_alternativo=True,
                )
                # Para econômico: escolher o que consome menos combustível
                if resultado_alternativo.litros_necessarios < resultado_principal.litros_necessarios:
                    resultados.append(resultado_alternativo)
                else:
                    resultados.append(resultado_principal)
            else:
                resultados.append(resultado_principal)

        # Filtrar apenas veículos que podem transportar
        resultados_viaveis = [r for r in resultados if r.pode_transportar]

        if not resultados_viaveis:
            return {
                "menor_custo": None,
                "mais_rapido": None,
                "melhor_custo_beneficio": None,
                "todos_resultados": resultados,
            }

        # Mais Econômico: menor consumo de combustível (litros)
        menor_custo = min(resultados_viaveis, key=lambda r: r.litros_necessarios)

        # Mais Rápido: menor tempo de viagem (maior velocidade)
        mais_rapido = min(resultados_viaveis, key=lambda r: r.tempo_viagem_horas)

        # Melhor Custo-Benefício: equilíbrio entre custo e tempo
        # Normalizar valores para comparação justa (0-1)
        if len(resultados_viaveis) > 1:
            custos = [r.custo_com_margem for r in resultados_viaveis]
            tempos = [r.tempo_viagem_horas for r in resultados_viaveis]

            custo_min, custo_max = min(custos), max(custos)
            tempo_min, tempo_max = min(tempos), max(tempos)

            # Evitar divisão por zero
            custo_range = custo_max - custo_min if custo_max != custo_min else Decimal("1")
            tempo_range = tempo_max - tempo_min if tempo_max != tempo_min else Decimal("1")

            # Calcular score normalizado (quanto menor, melhor)
            def calcular_score(r):
                custo_norm = (r.custo_com_margem - custo_min) / custo_range
                tempo_norm = (r.tempo_viagem_horas - tempo_min) / tempo_range
                return custo_norm + tempo_norm  # Peso igual para custo e tempo

            melhor_custo_beneficio = min(resultados_viaveis, key=calcular_score)
        else:
            melhor_custo_beneficio = resultados_viaveis[0]

        return {
            "menor_custo": menor_custo,
            "mais_rapido": mais_rapido,
            "melhor_custo_beneficio": melhor_custo_beneficio,
            "todos_resultados": resultados,
        }

    def calcular_para_rota(
        self, rota: Rota, peso_carga_kg: Decimal, tempo_maximo_horas: Optional[Decimal] = None
    ) -> Dict[str, Optional[ResultadoCalculo]]:
        """
        Calcula custos para uma rota específica.

        Args:
            rota: Instância da rota
            peso_carga_kg: Peso da carga em kg
            tempo_maximo_horas: Tempo máximo em horas

        Returns:
            Dicionário com as melhores opções
        """
        return self.calcular_melhor_opcao(
            peso_carga_kg=peso_carga_kg,
            distancia_km=rota.distancia_km,
            tempo_maximo_horas=tempo_maximo_horas,
            pedagio_valor=rota.pedagio_valor,
        )
