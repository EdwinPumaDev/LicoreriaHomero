
from django import forms

from apps.ventas.models import Venta, DetalleVenta
from apps.productos.models import Producto


class VentaForm(forms.ModelForm):

    class Meta:
        model = Venta
        fields = [
            "metodo_pago",
            "descuento",
            "observaciones",
        ]

        widgets = {
            "metodo_pago": forms.Select(attrs={
                "class": "form-control",
            }),
            "descuento": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observaciones de la venta...",
            }),
        }


class ProductoSelect(forms.Select):

    def create_option(
        self,
        name,
        value,
        label,
        selected,
        index,
        subindex=None,
        attrs=None,
    ):
        option = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex=subindex,
            attrs=attrs,
        )

        if value:
            producto = getattr(value, "instance", None)

            if producto:
                option["attrs"]["data-precio"] = str(
                    producto.precio_venta
                )
                option["attrs"]["data-codigo"] = producto.codigo

        return option


class DetalleVentaForm(forms.ModelForm):

    class Meta:
        model = DetalleVenta
        fields = [
            "producto",
            "cantidad",
            "precio_unitario",
            "descuento",
        ]

        widgets = {
            "producto": ProductoSelect(attrs={
                "class": "form-control",
            }),
            "cantidad": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "step": "1",
                "value": "1",
            }),
            "precio_unitario": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "readonly": "readonly",
            }),
            "descuento": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "value": "0",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["producto"].queryset = (
            Producto.objects.filter(activo=True)
            .order_by("nombre")
        )

        self.fields["producto"].empty_label = "Selecciona un producto"

        self.fields["cantidad"].required = True
        self.fields["precio_unitario"].required = False
        self.fields["descuento"].required = False
