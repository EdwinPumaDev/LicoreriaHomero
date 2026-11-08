
from datetime import date
from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

# Excel
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

# PDF
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from apps.ventas.models import Venta, DetalleVenta
from apps.caja.models import IngresoCaja
from apps.usuarios.permisos import administrador_o_encargado


# ==========================================================
# FILTROS DE FECHAS
# ==========================================================

def obtener_filtros(request):
    hoy = timezone.localdate()

    fecha_inicio = request.GET.get("desde") or hoy.replace(day=1).isoformat()
    fecha_fin = request.GET.get("hasta") or hoy.isoformat()

    try:
        desde = date.fromisoformat(fecha_inicio)
        hasta = date.fromisoformat(fecha_fin)

        if desde > hasta:
            raise ValueError

    except ValueError:
        desde = hoy.replace(day=1)
        hasta = hoy
        fecha_inicio = desde.isoformat()
        fecha_fin = hasta.isoformat()

    return desde, hasta, fecha_inicio, fecha_fin


# ==========================================================
# OBTENER DATOS DE REPORTES
# ==========================================================

def obtener_datos_reportes(desde, hasta):

    ventas = Venta.objects.filter(
        estado=Venta.Estado.CONFIRMADA,
        fecha__date__gte=desde,
        fecha__date__lte=hasta,
    )

    ingresos = IngresoCaja.objects.filter(
        anulado=False,
        fecha__date__gte=desde,
        fecha__date__lte=hasta,
        venta__estado=Venta.Estado.CONFIRMADA,
    )

    total_ventas = ventas.aggregate(
        total=Coalesce(Sum("total"), Decimal("0.00"))
    )["total"]

    cantidad_ventas = ventas.count()

    total_ingresos = ingresos.aggregate(
        total=Coalesce(Sum("monto"), Decimal("0.00"))
    )["total"]

    costos = DetalleVenta.objects.filter(
        venta__in=ventas
    ).aggregate(
        total=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("costo_unitario") * F("cantidad"),
                    output_field=DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                )
            ),
            Decimal("0.00"),
        )
    )["total"]

    utilidad = total_ventas - costos

    metodos_pago = (
        ingresos.values("metodo_pago")
        .annotate(
            cantidad=Count("id"),
            total=Sum("monto"),
        )
        .order_by("-total")
    )

    productos_mas_vendidos = (
        DetalleVenta.objects.filter(
            venta__in=ventas
        )
        .values(
            "producto__codigo",
            "producto__nombre",
        )
        .annotate(
            cantidad=Sum("cantidad"),
            total=Sum("subtotal"),
        )
        .order_by("-cantidad")[:10]
    )

    ventas_por_dia = (
        ventas.values("fecha__date")
        .annotate(
            cantidad=Count("id"),
            total=Sum("total"),
        )
        .order_by("fecha__date")
    )

    grafico_ventas_labels = [
        dia["fecha__date"].strftime("%d/%m/%Y")
        for dia in ventas_por_dia
    ]

    grafico_ventas_valores = [
        float(dia["total"] or 0)
        for dia in ventas_por_dia
    ]

    nombres_metodos = dict(Venta.MetodoPago.choices)

    grafico_metodos_labels = [
        nombres_metodos.get(
            metodo["metodo_pago"],
            metodo["metodo_pago"],
        )
        for metodo in metodos_pago
    ]

    grafico_metodos_valores = [
        float(metodo["total"] or 0)
        for metodo in metodos_pago
    ]

    return {
        "total_ventas": total_ventas,
        "cantidad_ventas": cantidad_ventas,
        "total_ingresos": total_ingresos,
        "total_costos": costos,
        "utilidad": utilidad,
        "metodos_pago": metodos_pago,
        "productos_mas_vendidos": productos_mas_vendidos,
        "ventas_por_dia": ventas_por_dia,
        "grafico_ventas_labels": grafico_ventas_labels,
        "grafico_ventas_valores": grafico_ventas_valores,
        "grafico_metodos_labels": grafico_metodos_labels,
        "grafico_metodos_valores": grafico_metodos_valores,
    }


# ==========================================================
# DASHBOARD DE REPORTES
# ==========================================================

@login_required
@administrador_o_encargado
def dashboard_reportes(request):

    desde, hasta, fecha_inicio, fecha_fin = obtener_filtros(request)

    contexto = obtener_datos_reportes(desde, hasta)

    contexto.update({
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    })

    return render(
        request,
        "reportes/dashboard.html",
        contexto,
    )


# ==========================================================
# EXPORTAR REPORTES A PDF
# ==========================================================

@login_required
@administrador_o_encargado
def exportar_pdf(request):

    desde, hasta, fecha_inicio, fecha_fin = obtener_filtros(request)

    datos = obtener_datos_reportes(desde, hasta)

    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title="Reporte de Licorería Homero",
        author="Licorería Homero",
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloHomero",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=24,
        textColor=colors.HexColor("#701E32"),
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitulo = ParagraphStyle(
        "SubtituloHomero",
        parent=estilos["Normal"],
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
    )

    encabezado = ParagraphStyle(
        "EncabezadoHomero",
        parent=estilos["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#701E32"),
        spaceBefore=12,
        spaceAfter=8,
    )

    normal = ParagraphStyle(
        "TextoHomero",
        parent=estilos["Normal"],
        fontSize=9,
        leading=12,
    )

    contenido = []

    contenido.append(Paragraph("LICORERÍA HOMERO", titulo))
    contenido.append(Paragraph("INFORME GENERAL DE REPORTES", subtitulo))
    contenido.append(Spacer(1, 8))

    contenido.append(Paragraph(
        f"Periodo: {desde.strftime('%d/%m/%Y')} al {hasta.strftime('%d/%m/%Y')}",
        subtitulo,
    ))

    contenido.append(Paragraph(
        f"Generado el: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}",
        subtitulo,
    ))

    contenido.append(Spacer(1, 20))

    # RESUMEN GENERAL

    contenido.append(Paragraph("1. RESUMEN GENERAL", encabezado))

    resumen = [
        ["Indicador", "Resultado"],
        ["Ventas confirmadas", str(datos["cantidad_ventas"])],
        ["Total vendido", f"Bs {datos['total_ventas']:,.2f}"],
        ["Costos de productos", f"Bs {datos['total_costos']:,.2f}"],
        ["Utilidad estimada", f"Bs {datos['utilidad']:,.2f}"],
        ["Ingresos válidos de caja", f"Bs {datos['total_ingresos']:,.2f}"],
    ]

    tabla_resumen = Table(
        resumen,
        colWidths=[9 * cm, 7 * cm],
    )

    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#701E32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F8F5F6"),
        ]),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    contenido.append(tabla_resumen)

    # PRODUCTOS MÁS VENDIDOS

    contenido.append(Paragraph("2. PRODUCTOS MÁS VENDIDOS", encabezado))

    filas_productos = [
        ["Código", "Producto", "Cantidad", "Total"]
    ]

    for producto in datos["productos_mas_vendidos"]:
        filas_productos.append([
            str(producto["producto__codigo"]),
            Paragraph(
                escape(str(producto["producto__nombre"])),
                normal,
            ),
            str(producto["cantidad"]),
            f"Bs {producto['total']:,.2f}",
        ])

    if len(filas_productos) == 1:
        filas_productos.append(["-", "Sin registros", "-", "-"])

    tabla_productos = Table(
        filas_productos,
        colWidths=[3 * cm, 7 * cm, 2.5 * cm, 3.5 * cm],
        repeatRows=1,
    )

    tabla_productos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#701E32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F8F5F6"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    contenido.append(tabla_productos)

    # MÉTODOS DE PAGO

    contenido.append(Paragraph("3. INGRESOS POR MÉTODO DE PAGO", encabezado))

    filas_metodos = [
        ["Método de pago", "Operaciones", "Total"]
    ]

    nombres_metodos = dict(Venta.MetodoPago.choices)

    for metodo in datos["metodos_pago"]:
        filas_metodos.append([
            nombres_metodos.get(
                metodo["metodo_pago"],
                metodo["metodo_pago"],
            ),
            str(metodo["cantidad"]),
            f"Bs {metodo['total']:,.2f}",
        ])

    if len(filas_metodos) == 1:
        filas_metodos.append(["Sin registros", "0", "Bs 0.00"])

    tabla_metodos = Table(
        filas_metodos,
        colWidths=[7 * cm, 4 * cm, 5 * cm],
    )

    tabla_metodos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#701E32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F8F5F6"),
        ]),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    contenido.append(tabla_metodos)

    # VENTAS POR DÍA

    contenido.append(Paragraph("4. RESUMEN DE VENTAS POR DÍA", encabezado))

    filas_dias = [
        ["Fecha", "Ventas realizadas", "Total vendido"]
    ]

    for dia in datos["ventas_por_dia"]:
        filas_dias.append([
            dia["fecha__date"].strftime("%d/%m/%Y"),
            str(dia["cantidad"]),
            f"Bs {dia['total']:,.2f}",
        ])

    if len(filas_dias) == 1:
        filas_dias.append(["Sin registros", "0", "Bs 0.00"])

    tabla_dias = Table(
        filas_dias,
        colWidths=[6 * cm, 5 * cm, 5 * cm],
        repeatRows=1,
    )

    tabla_dias.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#701E32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F8F5F6"),
        ]),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    contenido.append(tabla_dias)

    contenido.append(Spacer(1, 20))

    contenido.append(Paragraph(
        "Documento generado por el sistema de gestión de Licorería Homero.",
        subtitulo,
    ))

    documento.build(contenido)

    pdf = buffer.getvalue()
    buffer.close()

    respuesta = HttpResponse(
        pdf,
        content_type="application/pdf",
    )

    nombre_archivo = (
        f"reporte_licoreria_homero_{fecha_inicio}_{fecha_fin}.pdf"
    )

    respuesta["Content-Disposition"] = (
        f'attachment; filename="{nombre_archivo}"'
    )

    return respuesta


# ==========================================================
# EXPORTAR REPORTES A EXCEL
# ==========================================================

@login_required
@administrador_o_encargado
def exportar_excel(request):

    desde, hasta, fecha_inicio, fecha_fin = obtener_filtros(request)

    datos = obtener_datos_reportes(desde, hasta)

    libro = Workbook()

    hoja_resumen = libro.active
    hoja_resumen.title = "Resumen general"

    hoja_productos = libro.create_sheet("Productos")
    hoja_metodos = libro.create_sheet("Métodos de pago")
    hoja_dias = libro.create_sheet("Ventas por día")

    vino = "701E32"
    blanco = "FFFFFF"
    gris = "F8F5F6"

    borde = Side(style="thin", color="DDDDDD")

    formato_moneda = '"Bs " #,##0.00'

    # PREPARAR HOJAS

    def preparar_hoja(hoja, titulo, encabezados):

        hoja.sheet_view.showGridLines = False

        hoja.merge_cells(
            start_row=1,
            start_column=1,
            end_row=1,
            end_column=len(encabezados),
        )

        celda = hoja.cell(row=1, column=1, value=titulo)

        celda.font = Font(
            name="Arial",
            size=16,
            bold=True,
            color=vino,
        )

        celda.alignment = Alignment(horizontal="center")

        hoja.merge_cells(
            start_row=2,
            start_column=1,
            end_row=2,
            end_column=len(encabezados),
        )

        celda = hoja.cell(
            row=2,
            column=1,
            value=(
                f"Periodo: {desde.strftime('%d/%m/%Y')} "
                f"al {hasta.strftime('%d/%m/%Y')}"
            ),
        )

        celda.font = Font(italic=True)
        celda.alignment = Alignment(horizontal="center")

        for columna, texto in enumerate(encabezados, start=1):

            celda = hoja.cell(
                row=4,
                column=columna,
                value=texto,
            )

            celda.font = Font(bold=True, color=blanco)
            celda.fill = PatternFill("solid", fgColor=vino)

            celda.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )

            celda.border = Border(
                left=borde,
                right=borde,
                top=borde,
                bottom=borde,
            )

        hoja.freeze_panes = "A5"

    # APLICAR ESTILOS

    def aplicar_estilos(hoja, ultima_fila, columnas):

        for fila in range(5, ultima_fila + 1):

            for columna in range(1, columnas + 1):

                celda = hoja.cell(
                    row=fila,
                    column=columna,
                )

                celda.border = Border(
                    left=borde,
                    right=borde,
                    top=borde,
                    bottom=borde,
                )

                if fila % 2 == 1:
                    celda.fill = PatternFill(
                        "solid",
                        fgColor=gris,
                    )

                celda.alignment = Alignment(
                    vertical="center",
                )

        if ultima_fila >= 5:

            hoja.auto_filter.ref = (
                f"A4:{get_column_letter(columnas)}{ultima_fila}"
            )

    # ------------------------------------------------------
    # HOJA 1: RESUMEN GENERAL
    # ------------------------------------------------------

    preparar_hoja(
        hoja_resumen,
        "LICORERÍA HOMERO - INFORME GENERAL",
        ["Indicador", "Resultado"],
    )

    resumen = [
        ["Ventas confirmadas", datos["cantidad_ventas"]],
        ["Total vendido", float(datos["total_ventas"] or 0)],
        ["Costos de productos", float(datos["total_costos"] or 0)],
        ["Utilidad estimada", float(datos["utilidad"] or 0)],
        ["Ingresos válidos de caja", float(datos["total_ingresos"] or 0)],
    ]

    for fila, valores in enumerate(resumen, start=5):

        hoja_resumen.cell(
            row=fila,
            column=1,
            value=valores[0],
        )

        celda = hoja_resumen.cell(
            row=fila,
            column=2,
            value=valores[1],
        )

        if valores[0] != "Ventas confirmadas":
            celda.number_format = formato_moneda

    aplicar_estilos(hoja_resumen, 9, 2)

    hoja_resumen.column_dimensions["A"].width = 35
    hoja_resumen.column_dimensions["B"].width = 22

    # ------------------------------------------------------
    # HOJA 2: PRODUCTOS MÁS VENDIDOS
    # ------------------------------------------------------

    preparar_hoja(
        hoja_productos,
        "PRODUCTOS MÁS VENDIDOS",
        ["Código", "Producto", "Cantidad", "Total vendido"],
    )

    if datos["productos_mas_vendidos"]:

        for fila, producto in enumerate(
            datos["productos_mas_vendidos"],
            start=5,
        ):

            hoja_productos.cell(
                row=fila,
                column=1,
                value=producto["producto__codigo"] or "",
            )

            hoja_productos.cell(
                row=fila,
                column=2,
                value=producto["producto__nombre"] or "",
            )

            hoja_productos.cell(
                row=fila,
                column=3,
                value=producto["cantidad"] or 0,
            )

            celda = hoja_productos.cell(
                row=fila,
                column=4,
                value=float(producto["total"] or 0),
            )

            celda.number_format = formato_moneda

        ultima = 4 + len(datos["productos_mas_vendidos"])

    else:

        hoja_productos.cell(
            row=5,
            column=2,
            value="Sin registros",
        )

        ultima = 5

    aplicar_estilos(hoja_productos, ultima, 4)

    hoja_productos.column_dimensions["A"].width = 22
    hoja_productos.column_dimensions["B"].width = 48
    hoja_productos.column_dimensions["C"].width = 14
    hoja_productos.column_dimensions["D"].width = 20

    # ------------------------------------------------------
    # HOJA 3: MÉTODOS DE PAGO
    # ------------------------------------------------------

    preparar_hoja(
        hoja_metodos,
        "INGRESOS POR MÉTODO DE PAGO",
        ["Método de pago", "Operaciones", "Total"],
    )

    nombres_metodos = dict(Venta.MetodoPago.choices)

    if datos["metodos_pago"]:

        for fila, metodo in enumerate(
            datos["metodos_pago"],
            start=5,
        ):

            nombre = nombres_metodos.get(
                metodo["metodo_pago"],
                metodo["metodo_pago"],
            )

            hoja_metodos.cell(
                row=fila,
                column=1,
                value=nombre,
            )

            hoja_metodos.cell(
                row=fila,
                column=2,
                value=metodo["cantidad"] or 0,
            )

            celda = hoja_metodos.cell(
                row=fila,
                column=3,
                value=float(metodo["total"] or 0),
            )

            celda.number_format = formato_moneda

        ultima = 4 + len(datos["metodos_pago"])

    else:

        hoja_metodos.cell(
            row=5,
            column=1,
            value="Sin registros",
        )

        hoja_metodos.cell(
            row=5,
            column=2,
            value=0,
        )

        celda = hoja_metodos.cell(
            row=5,
            column=3,
            value=0,
        )

        celda.number_format = formato_moneda

        ultima = 5

    aplicar_estilos(hoja_metodos, ultima, 3)

    hoja_metodos.column_dimensions["A"].width = 28
    hoja_metodos.column_dimensions["B"].width = 18
    hoja_metodos.column_dimensions["C"].width = 20

    # ------------------------------------------------------
    # HOJA 4: VENTAS POR DÍA
    # ------------------------------------------------------

    preparar_hoja(
        hoja_dias,
        "RESUMEN DE VENTAS POR DÍA",
        ["Fecha", "Ventas realizadas", "Total vendido"],
    )

    if datos["ventas_por_dia"]:

        for fila, dia in enumerate(
            datos["ventas_por_dia"],
            start=5,
        ):

            celda_fecha = hoja_dias.cell(
                row=fila,
                column=1,
                value=dia["fecha__date"],
            )

            celda_fecha.number_format = "dd/mm/yyyy"

            hoja_dias.cell(
                row=fila,
                column=2,
                value=dia["cantidad"] or 0,
            )

            celda = hoja_dias.cell(
                row=fila,
                column=3,
                value=float(dia["total"] or 0),
            )

            celda.number_format = formato_moneda

        ultima = 4 + len(datos["ventas_por_dia"])

    else:

        hoja_dias.cell(
            row=5,
            column=1,
            value="Sin registros",
        )

        hoja_dias.cell(
            row=5,
            column=2,
            value=0,
        )

        celda = hoja_dias.cell(
            row=5,
            column=3,
            value=0,
        )

        celda.number_format = formato_moneda

        ultima = 5

    aplicar_estilos(hoja_dias, ultima, 3)

    hoja_dias.column_dimensions["A"].width = 20
    hoja_dias.column_dimensions["B"].width = 22
    hoja_dias.column_dimensions["C"].width = 20

    # ------------------------------------------------------
    # GENERAR ARCHIVO EXCEL
    # ------------------------------------------------------

    buffer = BytesIO()

    libro.save(buffer)

    buffer.seek(0)

    respuesta = HttpResponse(
        buffer.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    nombre_archivo = (
        f"reporte_licoreria_homero_{fecha_inicio}_{fecha_fin}.xlsx"
    )

    respuesta["Content-Disposition"] = (
        f'attachment; filename="{nombre_archivo}"'
    )

    buffer.close()

    return respuesta
