
from django.contrib import admin

from apps.auditoria.models import RegistroAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "usuario",
        "tipo_accion",
        "modulo",
        "descripcion",
        "direccion_ip",
        "fecha_hora",
    )

    list_filter = (
        "tipo_accion",
        "modulo",
        "fecha_hora",
    )

    search_fields = (
        "usuario__username",
        "modulo",
        "descripcion",
        "direccion_ip",
    )

    readonly_fields = (
        "usuario",
        "tipo_accion",
        "modulo",
        "descripcion",
        "direccion_ip",
        "fecha_hora",
    )

    ordering = ("-fecha_hora",)

    date_hierarchy = "fecha_hora"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
