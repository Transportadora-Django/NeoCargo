"""
Models para gerenciamento de cidades e rotas.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Estado(models.TextChoices):
    """Estados do Brasil."""

    AC = "AC", "Acre"
    AL = "AL", "Alagoas"
    AP = "AP", "Amapá"
    AM = "AM", "Amazonas"
    BA = "BA", "Bahia"
    CE = "CE", "Ceará"
    DF = "DF", "Distrito Federal"
    ES = "ES", "Espírito Santo"
    GO = "GO", "Goiás"
    MA = "MA", "Maranhão"
    MT = "MT", "Mato Grosso"
    MS = "MS", "Mato Grosso do Sul"
    MG = "MG", "Minas Gerais"
    PA = "PA", "Pará"
    PB = "PB", "Paraíba"
    PR = "PR", "Paraná"
    PE = "PE", "Pernambuco"
    PI = "PI", "Piauí"
    RJ = "RJ", "Rio de Janeiro"
    RN = "RN", "Rio Grande do Norte"
    RS = "RS", "Rio Grande do Sul"
    RO = "RO", "Rondônia"
    RR = "RR", "Roraima"
    SC = "SC", "Santa Catarina"
    SP = "SP", "São Paulo"
    SE = "SE", "Sergipe"
    TO = "TO", "Tocantins"


class Cidade(models.Model):
    """Modelo para representar cidades atendidas pela transportadora."""

    nome = models.CharField(max_length=100, verbose_name="Nome da Cidade")
    estado = models.CharField(max_length=2, choices=Estado.choices, verbose_name="Estado")

    # Coordenadas para exibir no mapa
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Latitude",
        help_text="Coordenada geográfica (ex: -23.5505199)",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Longitude",
        help_text="Coordenada geográfica (ex: -46.6333094)",
    )

    ativa = models.BooleanField(default=True, verbose_name="Cidade Ativa", help_text="Cidade está ativa para operação")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        ordering = ["estado", "nome"]
        unique_together = ["nome", "estado"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["ativa"]),
        ]

    def __str__(self):
        return f"{self.nome} - {self.estado}"

    @property
    def nome_completo(self):
        """Retorna nome completo da cidade com estado."""
        return f"{self.nome}/{self.estado}"


class Rota(models.Model):
    """Modelo para representar rotas entre cidades."""

    origem = models.ForeignKey(
        Cidade, on_delete=models.CASCADE, related_name="rotas_origem", verbose_name="Cidade de Origem"
    )
    destino = models.ForeignKey(
        Cidade, on_delete=models.CASCADE, related_name="rotas_destino", verbose_name="Cidade de Destino"
    )

    distancia_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Distância (km)",
        help_text="Distância em quilômetros entre as cidades",
    )

    tempo_estimado_horas = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
        blank=True,
        verbose_name="Tempo Estimado (horas)",
        help_text="Tempo estimado de viagem em horas",
    )

    pedagio_valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor do Pedágio (R$)",
        help_text="Valor total de pedágios na rota",
    )

    ativa = models.BooleanField(default=True, verbose_name="Rota Ativa", help_text="Rota está ativa para operação")

    observacoes = models.TextField(
        blank=True, null=True, verbose_name="Observações", help_text="Informações adicionais sobre a rota"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Rota"
        verbose_name_plural = "Rotas"
        ordering = ["origem__nome", "destino__nome"]
        unique_together = ["origem", "destino"]
        indexes = [
            models.Index(fields=["origem", "destino"]),
            models.Index(fields=["ativa"]),
        ]

    def __str__(self):
        return f"{self.origem.nome_completo} → {self.destino.nome_completo} ({self.distancia_km} km)"

    def clean(self):
        """Validação customizada."""
        from django.core.exceptions import ValidationError

        if self.origem == self.destino:
            raise ValidationError("A cidade de origem não pode ser igual à cidade de destino.")

    def save(self, *args, **kwargs):
        """Override do save para executar validação."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def custo_estimado_combustivel(self):
        """Calcula custo estimado de combustível (média de R$ 0.80/km)."""
        return self.distancia_km * Decimal("0.80")

    @property
    def custo_total_estimado(self):
        """Calcula custo total estimado (combustível + pedágio)."""
        return self.custo_estimado_combustivel + self.pedagio_valor


class ConfiguracaoPreco(models.Model):
    """Modelo para armazenar configurações de preços de combustível e margem de lucro."""

    preco_alcool = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=Decimal("3.499"),
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Preço do Álcool (R$/L)",
        help_text="Preço por litro de álcool",
    )

    preco_gasolina = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=Decimal("4.449"),
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Preço da Gasolina (R$/L)",
        help_text="Preço por litro de gasolina",
    )

    preco_diesel = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=Decimal("3.869"),
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Preço do Diesel (R$/L)",
        help_text="Preço por litro de diesel",
    )

    margem_lucro = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Margem de Lucro (%)",
        help_text="Margem de lucro em porcentagem",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Configuração de Preço"
        verbose_name_plural = "Configurações de Preços"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Configuração de Preços - {self.updated_at.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def get_atual(cls):
        """Retorna a configuração mais recente ou cria uma nova com valores padrão."""
        config = cls.objects.first()
        if not config:
            config = cls.objects.create()
        return config
