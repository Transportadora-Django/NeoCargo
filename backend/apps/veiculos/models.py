from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TipoVeiculo(models.TextChoices):
    """Tipos de veículos disponíveis"""

    CARRETA = "carreta", "Carreta"
    VAN = "van", "Van"
    CARRO = "carro", "Carro"
    MOTO = "moto", "Moto"


class TipoCombustivel(models.TextChoices):
    """Tipos de combustível"""

    DIESEL = "diesel", "Diesel"
    GASOLINA = "gasolina", "Gasolina"
    ALCOOL = "alcool", "Álcool"


class EspecificacaoVeiculo(models.Model):
    """Especificações técnicas dos tipos de veículo (predefinidas)"""

    tipo = models.CharField(max_length=20, choices=TipoVeiculo.choices, unique=True, verbose_name="Tipo de Veículo")
    combustivel_principal = models.CharField(
        max_length=20, choices=TipoCombustivel.choices, verbose_name="Combustível Principal"
    )
    combustivel_alternativo = models.CharField(
        max_length=20, choices=TipoCombustivel.choices, blank=True, null=True, verbose_name="Combustível Alternativo"
    )
    rendimento_principal = models.FloatField(
        verbose_name="Rendimento Principal (Km/L)", validators=[MinValueValidator(0.1)]
    )
    rendimento_alternativo = models.FloatField(
        blank=True, null=True, verbose_name="Rendimento Alternativo (Km/L)", validators=[MinValueValidator(0.1)]
    )
    carga_maxima = models.FloatField(verbose_name="Carga Máxima (Kg)", validators=[MinValueValidator(1)])
    velocidade_media = models.IntegerField(
        verbose_name="Velocidade Média (Km/h)", validators=[MinValueValidator(1), MaxValueValidator(200)]
    )
    reducao_rendimento_principal = models.FloatField(
        verbose_name="Redução de Rendimento por Kg (Principal)",
        help_text="Redução no rendimento por cada Kg de carga",
        validators=[MinValueValidator(0)],
    )
    reducao_rendimento_alternativo = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Redução de Rendimento por Kg (Alternativo)",
        help_text="Redução no rendimento por cada Kg de carga com combustível alternativo",
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Especificação de Veículo"
        verbose_name_plural = "Especificações de Veículos"
        ordering = ["tipo"]

    def __str__(self):
        return f"{self.get_tipo_display()}"


class Veiculo(models.Model):
    """Veículo da empresa (instância real)"""

    especificacao = models.ForeignKey(
        EspecificacaoVeiculo, on_delete=models.PROTECT, verbose_name="Tipo de Veículo", related_name="veiculos"
    )
    marca = models.CharField(max_length=50, verbose_name="Marca", help_text="Ex: Ford, Scania, Honda, etc.")
    modelo = models.CharField(
        max_length=100, verbose_name="Modelo do Veículo", help_text="Ex: Transit, R450, CG 160, etc."
    )
    placa = models.CharField(max_length=10, unique=True, verbose_name="Placa")
    ano = models.IntegerField(
        verbose_name="Ano de Fabricação", validators=[MinValueValidator(1990), MaxValueValidator(2030)]
    )
    cor = models.CharField(max_length=50, verbose_name="Cor")
    ativo = models.BooleanField(
        default=True,
        verbose_name="Veículo Ativo",
        help_text="Veículos inativos não podem ser utilizados em novos pedidos",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"
