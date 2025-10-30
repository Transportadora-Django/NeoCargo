from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.contas.models import Role
from apps.veiculos.models import TipoVeiculo


class ConfiguracaoSistema(models.Model):
    """Configurações gerais do sistema"""

    solicitacoes_abertas = models.BooleanField(
        default=True,
        verbose_name="Solicitações Abertas",
        help_text="Define se o sistema está aceitando novas solicitações de mudança de perfil",
    )
    mensagem_solicitacoes_fechadas = models.TextField(
        default="No momento não estamos aceitando novas solicitações. Tente novamente mais tarde.",
        verbose_name="Mensagem quando fechado",
        help_text="Mensagem exibida quando as solicitações estão fechadas",
    )
    atualizado_em = models.DateTimeField(auto_now=True)
    atualizado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="configuracoes_atualizadas"
    )

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"

    def __str__(self):
        status = "Abertas" if self.solicitacoes_abertas else "Fechadas"
        return f"Solicitações: {status}"

    @classmethod
    def get_config(cls):
        """Retorna ou cria a configuração única do sistema"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class StatusSolicitacao(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    APROVADA = "aprovada", "Aprovada"
    REJEITADA = "rejeitada", "Rejeitada"


class CategoriaCNH(models.TextChoices):
    """Categorias de CNH"""

    B = "B", "Categoria B"
    C = "C", "Categoria C"
    D = "D", "Categoria D"
    E = "E", "Categoria E"


class SolicitacaoMudancaPerfil(models.Model):
    """Solicitações de mudança de perfil de usuário"""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solicitacoes_mudanca")
    role_atual = models.CharField(max_length=20, choices=Role.choices, verbose_name="Role Atual")
    role_solicitada = models.CharField(max_length=20, choices=Role.choices, verbose_name="Role Solicitada")
    justificativa = models.TextField(verbose_name="Justificativa", help_text="Explique por que deseja mudar de perfil")

    # Campos específicos para motorista
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")

    # Novos campos para NC-38 (motoristas)
    cnh_categoria = models.CharField(
        max_length=1,
        choices=CategoriaCNH.choices,
        blank=True,
        null=True,
        verbose_name="Categoria CNH",
        help_text="Categoria da Carteira Nacional de Habilitação",
    )
    sede_atual = models.ForeignKey(
        "rotas.Cidade",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Sede Atual",
        help_text="Cidade onde o motorista estará disponível",
    )

    # Dados do veículo (DEPRECATED - veículos são da empresa)
    tipo_veiculo = models.CharField(
        max_length=20, choices=TipoVeiculo.choices, blank=True, null=True, verbose_name="Tipo de Veículo"
    )
    modelo_veiculo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo do Veículo")
    placa_veiculo = models.CharField(max_length=10, blank=True, null=True, verbose_name="Placa do Veículo")
    ano_veiculo = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Ano do Veículo",
        validators=[MinValueValidator(1990), MaxValueValidator(2030)],
    )
    cor_veiculo = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cor do Veículo")

    status = models.CharField(
        max_length=20, choices=StatusSolicitacao.choices, default=StatusSolicitacao.PENDENTE, verbose_name="Status"
    )
    observacoes_admin = models.TextField(blank=True, null=True, verbose_name="Observações do Administrador")
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitacoes_aprovadas",
        verbose_name="Aprovado por",
    )
    data_aprovacao = models.DateTimeField(blank=True, null=True, verbose_name="Data de Aprovação")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Solicitação de Mudança de Perfil"
        verbose_name_plural = "Solicitações de Mudança de Perfil"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.usuario.username}: {self.get_role_atual_display()} → {self.get_role_solicitada_display()}"

    @property
    def is_pendente(self):
        return self.status == StatusSolicitacao.PENDENTE

    @property
    def is_aprovada(self):
        return self.status == StatusSolicitacao.APROVADA

    @property
    def is_rejeitada(self):
        return self.status == StatusSolicitacao.REJEITADA
