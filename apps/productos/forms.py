from django import forms
from apps.productos.models import Producto, Categoria, Marca


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "codigo",
            "codigo_barras",
            "nombre",
            "descripcion",
            "categoria",
            "marca",
            "unidad_medida",
            "costo",
            "precio_venta",
            "stock",
            "stock_minimo",
            "imagen",
            "activo",
        ]
        widgets = {
            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej. SING-CR-750",
                    "required": True,
                }
            ),
            "codigo_barras": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Escanee o digite código de barras (opcional)",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre completo del producto",
                    "required": True,
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notas sobre volumen, añejamiento, presentación, etc.",
                }
            ),
            "categoria": forms.Select(attrs={"class": "form-select", "required": True}),
            "marca": forms.Select(attrs={"class": "form-select"}),
            "unidad_medida": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "costo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.10",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "precio_venta": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.10",
                    "min": "0",
                    "placeholder": "0.00",
                    "required": True,
                }
            ),
            "stock": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "placeholder": "0"}
            ),
            "stock_minimo": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "placeholder": "5"}
            ),
            "imagen": forms.FileInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de categoría (Ej. Vinos de Altura)",
                    "required": True,
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Breve descripción",
                }
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de marca (Ej. Casa Real)",
                    "required": True,
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Breve descripción",
                }
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
