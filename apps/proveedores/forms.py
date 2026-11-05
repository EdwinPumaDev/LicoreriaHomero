from django import forms
from apps.proveedores.models import Proveedor


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            "nombre",
            "nit",
            "persona_contacto",
            "telefono",
            "correo",
            "direccion",
            "observaciones",
            "activo",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Razón social o nombre de la empresa / distribuidora",
                    "required": True,
                }
            ),
            "nit": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "NIT del proveedor (Ej. 1023849021)",
                }
            ),
            "persona_contacto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del ejecutivo o vendedor asignado",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Teléfono / Celular (Ej. 71234567)",
                }
            ),
            "correo": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "correo@proveedor.com",
                }
            ),
            "direccion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dirección física o almacén de distribución",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Días de entrega, condiciones comerciales, crédito, etc.",
                }
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
