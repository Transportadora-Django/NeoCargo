from django.contrib.auth.models import User
from django.db import models
from apps.contas.models import Role


class SolicitacaoMudancaPerfil(models.Model):
    """
    Modelo para armazenar solicitações de mudança de perfil de usuário.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="solicitacoes_mudanca_perfil", verbose_name="Usuário"
    )
    perfil_atual = models.CharField(max_length=20, choices=Role.choices, verbose_name="Perfil Atual")
    perfil_solicitado = models.CharField(max_length=20, choices=Role.choices, verbose_name="Perfil Solicitado")
    justificativa = models.TextField(
        verbose_name="Justificativa", help_text="Explique o motivo da solicitação de mudança de perfil"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pendente", "Pendente"),
            ("aprovada", "Aprovada"),
            ("rejeitada", "Rejeitada"),
        ],
        default="pendente",
        verbose_name="Status",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    # Campos para aprovação/rejeição
    aprovada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="aprovacoes_mudanca_perfil",
        verbose_name="Aprovada por",
    )
    observacoes_aprovacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações da Aprovação",
        help_text="Observações do gerente/owner sobre a decisão",
    )

    class Meta:
        verbose_name = "Solicitação de Mudança de Perfil"
        verbose_name_plural = "Solicitações de Mudança de Perfil"
        ordering = ["-created_at"]

    def __str__(self):
        nome = self.user.get_full_name() or self.user.username
        return f"{nome}: {self.get_perfil_atual_display()} → {self.get_perfil_solicitado_display()}"

    @property
    def is_pendente(self):
        return self.status == "pendente"

    @property
    def is_aprovada(self):
        return self.status == "aprovada"

    @property
    def is_rejeitada(self):
        return self.status == "rejeitada"
