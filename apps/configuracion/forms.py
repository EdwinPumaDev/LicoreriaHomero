from django import forms

from apps.configuracion.models import ConfiguracionSistema


class ConfiguracionSistemaForm(forms.ModelForm):

    class Meta:
        model = ConfiguracionSistema

        fields = [
            "nombre_comercial",
            "nombre_sistema",
            "logo",
            "favicon",
            "propietario",
            "nit",
            "direccion",
            "telefono",
            "color_principal",
            "color_secundario",
            "color_fondo",
            "color_texto",
            "tipografia",
            "tema",
        ]

        widgets = {
            "nombre_comercial": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del negocio",
            }),
            "nombre_sistema": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del sistema",
            }),
            "logo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "favicon": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "propietario": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del propietario",
            }),
            "nit": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Número de NIT",
            }),
            "direccion": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Dirección del negocio",
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono de contacto",
            }),
            "color_principal": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color",
            }),
            "color_secundario": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color",
            }),
            "color_fondo": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color",
            }),
            "color_texto": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color",
            }),
            "tipografia": forms.Select(
                choices=[
                    ("Inter", "Inter"),
                    ("Arial", "Arial"),
                    ("Roboto", "Roboto"),
                    ("Poppins", "Poppins"),
                    ("Open Sans", "Open Sans"),
                    ("Montserrat", "Montserrat"),
                ],
                attrs={"class": "form-control"},
            ),
            "tema": forms.Select(attrs={
                "class": "form-control",
            }),
        }