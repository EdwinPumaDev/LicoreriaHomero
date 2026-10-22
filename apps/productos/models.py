
from django.db import models
from django.core.validators import MinValueValidator


class Categoria(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categorias"
        ordering = ["nombre"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "marcas"
        ordering = ["nombre"]
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class UnidadMedida(models.TextChoices):
        UNIDAD = "UNIDAD", "Unidad"
        BOTELLA = "BOTELLA", "Botella"
        LATA = "LATA", "Lata"
        PAQUETE = "PAQUETE", "Paquete"
        CAJA = "CAJA", "Caja"
        BOLSA = "BOLSA", "Bolsa"

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del producto",
    )
    codigo_barras = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código de barras",
    )
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del producto",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="Categoría",
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
        verbose_name="Marca",
    )

    unidad_medida = models.CharField(
        max_length=20,
        choices=UnidadMedida.choices,
        default=UnidadMedida.UNIDAD,
        verbose_name="Unidad de medida",
    )

    costo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Costo de compra",
    )
    precio_venta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de venta",
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Existencias actuales",
    )
    stock_minimo = models.PositiveIntegerField(
        default=5,
        verbose_name="Stock mínimo",
    )

    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
        null=True,
        verbose_name="Imagen del producto",
    )

    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "productos"
        ordering = ["nombre"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def necesita_reposicion(self):
        return self.stock <= self.stock_minimo
