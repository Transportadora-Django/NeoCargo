from django.db import models
from apps.contas.models import Profile
from apps.rotas.models import Cidade
from apps.veiculos.models import Veiculo
from apps.pedidos.models import Pedido


class CategoriaCNH(models.TextChoices):
    """Categorias de CNH disponíveis"""

    B = "B", "Categoria B"
    C = "C", "Categoria C"
    D = "D", "Categoria D"
    E = "E", "Categoria E"


class Motorista(models.Model):
    """Modelo para motoristas com informações específicas"""

    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="motorista", verbose_name="Perfil de Usuário"
    )
    sede_atual = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT,
        related_name="motoristas",
        verbose_name="Sede Atual",
        help_text="Cidade onde o motorista está atualmente disponível",
    )
    cnh_categoria = models.CharField(
        max_length=1,
        choices=CategoriaCNH.choices,
        verbose_name="Categoria CNH",
        help_text="Categoria da Carteira Nacional de Habilitação",
    )
    disponivel = models.BooleanField(
        default=True, verbose_name="Disponível", help_text="Indica se o motorista está disponível para entregas"
    )
    entregas_concluidas = models.IntegerField(
        default=0, verbose_name="Entregas Concluídas", help_text="Contador de entregas realizadas com sucesso"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"
        ordering = ["-entregas_concluidas", "profile__user__first_name"]

    def __str__(self):
        nome = self.profile.user.get_full_name() or self.profile.user.username
        return f"{nome} - CNH {self.cnh_categoria} - {self.sede_atual.nome_completo}"


class StatusAtribuicao(models.TextChoices):
    """Status da atribuição de pedido"""

    PENDENTE = "pendente", "Pendente"
    EM_ANDAMENTO = "em_andamento", "Em Andamento"
    CONCLUIDO = "concluido", "Concluído"
    CANCELADO = "cancelado", "Cancelado"


class AtribuicaoPedido(models.Model):
    """Modelo para atribuição de motorista e veículo a pedidos"""

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="atribuicao", verbose_name="Pedido")
    motorista = models.ForeignKey(
        Motorista, on_delete=models.PROTECT, related_name="atribuicoes", verbose_name="Motorista"
    )
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name="atribuicoes", verbose_name="Veículo")
    status = models.CharField(
        max_length=20, choices=StatusAtribuicao.choices, default=StatusAtribuicao.PENDENTE, verbose_name="Status"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Atribuição de Pedido"
        verbose_name_plural = "Atribuições de Pedidos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pedido #{self.pedido.id} - {self.motorista.profile.user.username} - {self.veiculo.placa}"

    @property
    def is_pendente(self):
        return self.status == StatusAtribuicao.PENDENTE

    @property
    def is_em_andamento(self):
        return self.status == StatusAtribuicao.EM_ANDAMENTO

    @property
    def is_concluido(self):
        return self.status == StatusAtribuicao.CONCLUIDO

    @property
    def is_cancelado(self):
        return self.status == StatusAtribuicao.CANCELADO


class TipoProblema(models.TextChoices):
    """Tipos de problemas que podem ser reportados"""

    VEICULO = "veiculo", "Problema com Veículo"
    CARGA = "carga", "Problema com Carga"
    ROTA = "rota", "Problema na Rota"
    CLIENTE = "cliente", "Problema com Cliente"
    ACIDENTE = "acidente", "Acidente"
    OUTRO = "outro", "Outro"


class StatusProblema(models.TextChoices):
    """Status do problema reportado"""

    PENDENTE = "pendente", "Pendente"
    EM_ANALISE = "em_analise", "Em Análise"
    RESOLVIDO = "resolvido", "Resolvido"


class ProblemaEntrega(models.Model):
    """Modelo para problemas reportados pelos motoristas durante entregas"""

    atribuicao = models.ForeignKey(
        AtribuicaoPedido,
        on_delete=models.CASCADE,
        related_name="problemas",
        verbose_name="Atribuição",
        help_text="Atribuição de pedido relacionada ao problema",
    )
    tipo = models.CharField(
        max_length=20, choices=TipoProblema.choices, verbose_name="Tipo de Problema", help_text="Categoria do problema"
    )
    descricao = models.TextField(
        verbose_name="Descrição do Problema", help_text="Descrição detalhada do problema encontrado"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusProblema.choices,
        default=StatusProblema.PENDENTE,
        verbose_name="Status",
        help_text="Status atual do problema",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    resolvido_em = models.DateTimeField(null=True, blank=True, verbose_name="Resolvido em")
    resolucao = models.TextField(
        blank=True, null=True, verbose_name="Resolução", help_text="Descrição da resolução do problema"
    )

    class Meta:
        verbose_name = "Problema de Entrega"
        verbose_name_plural = "Problemas de Entrega"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} - Pedido #{self.atribuicao.pedido.id} - {self.get_status_display()}"

    @property
    def is_pendente(self):
        return self.status == StatusProblema.PENDENTE

    @property
    def is_em_analise(self):
        return self.status == StatusProblema.EM_ANALISE

    @property
    def is_resolvido(self):
        return self.status == StatusProblema.RESOLVIDO

    @property
    def motorista(self):
        """Atalho para acessar o motorista da atribuição"""
        return self.atribuicao.motorista

    @property
    def pedido(self):
        """Atalho para acessar o pedido da atribuição"""
        return self.atribuicao.pedido
