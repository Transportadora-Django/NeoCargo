from django.contrib.auth.models import User
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta


class Role(models.TextChoices):
    CLIENTE = "cliente", "Cliente"
    MOTORISTA = "motorista", "Motorista"
    GERENTE = "gerente", "Gerente"
    OWNER = "owner", "Owner"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENTE, verbose_name="Papel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"

    @property
    def is_cliente(self):
        return self.role == Role.CLIENTE

    @property
    def is_motorista(self):
        return self.role == Role.MOTORISTA

    @property
    def is_gerente(self):
        return self.role == Role.GERENTE

    @property
    def is_owner(self):
        return self.role == Role.OWNER


class EmailChangeRequest(models.Model):
    """
    Modelo para armazenar solicitações de mudança de email que precisam de confirmação.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_change_requests")
    old_email = models.EmailField(verbose_name="Email Antigo")
    new_email = models.EmailField(verbose_name="Email Novo")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Solicitação de Mudança de Email"
        verbose_name_plural = "Solicitações de Mudança de Email"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.old_email} → {self.new_email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expira em 24 horas
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.confirmed and not self.is_expired
