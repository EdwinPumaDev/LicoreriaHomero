
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from apps.usuarios.models import PerfilUsuario


class UsuarioCrearForm(forms.ModelForm):

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        validators=[validate_password],
    )

    password_confirmacion = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
    )

    cargo = forms.ChoiceField(
        label="Cargo",
        choices=PerfilUsuario.Cargo.choices,
    )

    telefono = forms.CharField(
        label="Teléfono",
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Correo electrónico",
        }

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirmacion = cleaned_data.get("password_confirmacion")

        if password and confirmacion and password != confirmacion:
            self.add_error(
                "password_confirmacion",
                "Las contraseñas no coinciden.",
            )

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.set_password(self.cleaned_data["password"])

        cargo = self.cleaned_data["cargo"]
        telefono = self.cleaned_data.get("telefono", "")

        usuario.is_staff = (
            cargo == PerfilUsuario.Cargo.ADMINISTRADOR
        )

        if commit:
            usuario.save()

            perfil, creado = PerfilUsuario.objects.get_or_create(
                usuario=usuario
            )

            perfil.cargo = cargo
            perfil.telefono = telefono
            perfil.activo = True
            perfil.save()

        return usuario


class UsuarioEditarForm(forms.ModelForm):

    cargo = forms.ChoiceField(
        label="Cargo",
        choices=PerfilUsuario.Cargo.choices,
    )

    telefono = forms.CharField(
        label="Teléfono",
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Correo electrónico",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        perfil = getattr(self.instance, "perfil", None)

        if perfil:
            self.fields["cargo"].initial = perfil.cargo
            self.fields["telefono"].initial = perfil.telefono

    def save(self, commit=True):
        usuario = super().save(commit=False)

        cargo = self.cleaned_data["cargo"]
        telefono = self.cleaned_data.get("telefono", "")

        usuario.is_staff = (
            cargo == PerfilUsuario.Cargo.ADMINISTRADOR
        )

        if commit:
            usuario.save()

            perfil, creado = PerfilUsuario.objects.get_or_create(
                usuario=usuario
            )

            perfil.cargo = cargo
            perfil.telefono = telefono
            perfil.save()

        return usuario


class UsuarioCambiarPasswordForm(forms.Form):

    password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        validators=[validate_password],
    )

    password_confirmacion = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirmacion = cleaned_data.get("password_confirmacion")

        if password and confirmacion and password != confirmacion:
            self.add_error(
                "password_confirmacion",
                "Las contraseñas no coinciden.",
            )

        return cleaned_data

    def guardar(self, usuario):
        usuario.set_password(self.cleaned_data["password"])
        usuario.save(update_fields=["password"])
        return usuario
