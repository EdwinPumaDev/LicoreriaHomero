from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from apps.usuarios.models import PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = "Perfil de la Licorería"
    fk_name = "usuario"


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = (
        "username",
        "first_name",
        "last_name",
        "get_cargo",
        "is_staff",
        "is_active",
    )

    @admin.display(description="Cargo en Licorería")
    def get_cargo(self, instance):
        if hasattr(instance, "perfil") and instance.perfil:
            return instance.perfil.get_cargo_display()
        return "Sin perfil"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cargo", "telefono", "activo", "creado_en")
    list_filter = ("cargo", "activo")
    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "telefono",
    )
    list_editable = ("cargo", "activo")
