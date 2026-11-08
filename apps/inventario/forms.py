
from django import forms

from apps.productos.models import Producto
from apps.inventario.models import MovimientoInventario


class AjusteInventarioForm(forms.Form):

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True).order_by("nombre"),
        label="Producto",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    tipo = forms.ChoiceField(
        choices=[
            (
                MovimientoInventario.Tipo.AJUSTE_ENTRADA,
                "Entrada de inventario",
            ),
            (
                MovimientoInventario.Tipo.AJUSTE_SALIDA,
                "Salida de inventario",
            ),
        ],
        label="Tipo de ajuste",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "Ingrese la cantidad",
            }
        ),
    )

    motivo = forms.CharField(
        max_length=250,
        label="Motivo del ajuste",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Explique por qué realiza este ajuste...",
            }
        ),
    )
