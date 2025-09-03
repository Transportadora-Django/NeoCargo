from django.contrib.auth.models import User
from django.db import models


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
