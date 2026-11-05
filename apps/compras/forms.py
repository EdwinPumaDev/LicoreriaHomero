from django import forms
from apps.compras.models import Compra


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ["proveedor", "numero_comprobante", "observaciones"]
        widgets = {
            "proveedor": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "numero_comprobante": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "N.º de Factura, Nota de Entrega o Recibo de compra",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Notas adicionales sobre el pedido, entrega o forma de pago...",
                }
            ),
        }
