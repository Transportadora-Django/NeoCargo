from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class StatusPedido(models.TextChoices):
    COTACAO = "cotacao", "Cotação Gerada"
    PENDENTE = "pendente", "Pendente"
    APROVADO = "aprovado", "Aprovado"
    RECUSADO = "recusado", "Recusado"
    CANCELADO = "cancelado", "Cancelado"
    EM_TRANSPORTE = "em_transporte", "Em Transporte"
    CONCLUIDO = "concluido", "Concluído"


class OpcaoCotacao(models.TextChoices):
    ECONOMICO = "economico", "Mais Econômico"
    RAPIDO = "rapido", "Mais Rápido"
    CUSTO_BENEFICIO = "custo_beneficio", "Melhor Custo-Benefício"


class Pedido(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pedidos", verbose_name="Cliente")

    cidade_origem = models.CharField(
        max_length=255, verbose_name="Cidade de Origem", help_text="Cidade de coleta da carga"
    )
    cidade_destino = models.CharField(
        max_length=255, verbose_name="Cidade de Destino", help_text="Cidade de entrega da carga"
    )
    peso_carga = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Peso da Carga (kg)",
        help_text="Peso total da carga em quilogramas",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    prazo_desejado = models.PositiveIntegerField(
        verbose_name="Prazo Desejado (dias)",
        help_text="Prazo máximo para entrega em dias",
        validators=[MinValueValidator(1)],
    )
    observacoes = models.TextField(
        blank=True, null=True, verbose_name="Observações", help_text="Informações adicionais sobre a carga (opcional)"
    )

    # Opção de cotação escolhida pelo cliente
    opcao = models.CharField(
        max_length=20,
        choices=OpcaoCotacao.choices,
        blank=True,
        null=True,
        verbose_name="Opção Escolhida",
        help_text="Opção de cotação selecionada pelo cliente",
    )

    # Cotações calculadas automaticamente
    cotacao_economico_valor = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor - Mais Econômico"
    )
    cotacao_economico_tempo = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Tempo (h) - Mais Econômico"
    )
    cotacao_economico_veiculo = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Veículo - Mais Econômico"
    )

    cotacao_rapido_valor = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor - Mais Rápido"
    )
    cotacao_rapido_tempo = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Tempo (h) - Mais Rápido"
    )
    cotacao_rapido_veiculo = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Veículo - Mais Rápido"
    )

    cotacao_custo_beneficio_valor = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor - Melhor Custo-Benefício"
    )
    cotacao_custo_beneficio_tempo = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Tempo (h) - Melhor Custo-Benefício"
    )
    cotacao_custo_beneficio_veiculo = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Veículo - Melhor Custo-Benefício"
    )

    # Campos que serão preenchidos pelo gerente posteriormente
    preco_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Preço Final",
        help_text="Preço calculado pelo gerente",
    )
    prazo_final = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Prazo Final", help_text="Prazo calculado pelo gerente"
    )
    veiculo_final = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Veículo Final", help_text="Veículo definido pelo gerente"
    )

    status = models.CharField(
        max_length=20, choices=StatusPedido.choices, default=StatusPedido.COTACAO, verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    numero_pedido_cliente = models.PositiveIntegerField(
        default=1,
        verbose_name="Número do Pedido (Cliente)",
        help_text="Número sequencial do pedido por cliente",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-created_at"]

    def __str__(self):
        nome = self.cliente.get_full_name() or self.cliente.username
        return f"Pedido #{self.id} - {nome} ({self.get_status_display()})"

    @property
    def is_cotacao(self):
        return self.status == StatusPedido.COTACAO

    @property
    def is_pendente(self):
        return self.status == StatusPedido.PENDENTE

    @property
    def is_cancelado(self):
        return self.status == StatusPedido.CANCELADO

    def pode_ser_cancelado(self):
        """Verifica se o pedido pode ser cancelado - apenas pedidos em cotação ou pendentes"""
        return self.status in [StatusPedido.COTACAO, StatusPedido.PENDENTE]

    def cancelar(self):
        """Cancela o pedido se possível - apenas pedidos pendentes"""
        if self.pode_ser_cancelado():
            self.status = StatusPedido.CANCELADO
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        # Auto-incrementar numero_pedido_cliente se for um novo pedido
        if not self.pk:
            ultimo_pedido = Pedido.objects.filter(cliente=self.cliente).order_by("-numero_pedido_cliente").first()
            if ultimo_pedido:
                self.numero_pedido_cliente = ultimo_pedido.numero_pedido_cliente + 1
            else:
                self.numero_pedido_cliente = 1
        super().save(*args, **kwargs)
