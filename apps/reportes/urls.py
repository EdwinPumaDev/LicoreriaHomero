from django.urls import path
from apps.reportes import views

app_name = "reportes"

urlpatterns = [
    path("", views.dashboard_reportes, name="dashboard"),

    path(
        "exportar-pdf/",
        views.exportar_pdf,
        name="exportar_pdf",
    ),

    path(
        "exportar-excel/",
        views.exportar_excel,
        name="exportar_excel",
    ),
]