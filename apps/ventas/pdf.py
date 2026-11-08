
from io import BytesIO
from xml.sax.saxutils import escape

from django.http import HttpResponse, Http404
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


BORGOÑA = colors.HexColor("#701E32")
GRIS = colors.HexColor("#66616A")
GRIS_CLARO = colors.HexColor("#F6F3F4")
GRIS_LINEA = colors.HexColor("#E8E2E4")


def generar_comprobante_pdf(request, pk):
    from apps.ventas.models import Venta

    try:
        venta = (
            Venta.objects
            .select_related("usuario")
            .prefetch_related("detalles__producto")
            .get(pk=pk)
        )
    except Venta.DoesNotExist:
        raise Http404("La venta no existe.")

    if venta.estado != Venta.Estado.CONFIRMADA:
        raise Http404("Solo se permiten comprobantes de ventas confirmadas.")

    detalles = list(venta.detalles.all())

    if not detalles:
        raise Http404("La venta no contiene productos.")

    buffer = BytesIO()

    descargar = request.GET.get("descargar") == "1"

    response = HttpResponse(content_type="application/pdf")

    tipo = "attachment" if descargar else "inline"

    response["Content-Disposition"] = (
        f'{tipo}; filename="comprobante_{venta.numero}.pdf"'
    )

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A5,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=11 * mm,
        bottomMargin=12 * mm,
        title=f"Comprobante de venta {venta.numero}",
        author="Licorería Homero",
    )

    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="Empresa",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        textColor=BORGOÑA,
        spaceAfter=3,
    ))

    estilos.add(ParagraphStyle(
        name="Subtitulo",
        parent=estilos["Normal"],
        fontSize=8,
        textColor=GRIS,
    ))

    estilos.add(ParagraphStyle(
        name="TituloPDF",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        alignment=TA_RIGHT,
        textColor=BORGOÑA,
    ))

    estilos.add(ParagraphStyle(
        name="NormalPDF",
        parent=estilos["Normal"],
        fontSize=8,
        leading=11,
        textColor=GRIS,
    ))

    estilos.add(ParagraphStyle(
        name="NegritaPDF",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#302B31"),
    ))

    estilos.add(ParagraphStyle(
        name="TablaPDF",
        parent=estilos["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#39343A"),
    ))

    estilos.add(ParagraphStyle(
        name="CabeceraTabla",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=8,
        alignment=TA_CENTER,
        textColor=colors.white,
    ))

    estilos.add(ParagraphStyle(
        name="TotalPDF",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=BORGOÑA,
        alignment=TA_RIGHT,
    ))

    elementos = []

    # ENCABEZADO

    marca = Table(
        [[Paragraph(
            "<font color='white'><b>H</b></font>",
            ParagraphStyle(
                "Marca",
                fontName="Helvetica-Bold",
                fontSize=19,
                alignment=TA_CENTER,
            ),
        )]],
        colWidths=[13 * mm],
        rowHeights=[13 * mm],
    )

    marca.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BORGOÑA),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    empresa = [
        marca,
        Paragraph("LICORERÍA HOMERO", estilos["Empresa"]),
        Paragraph("Sistema de gestión comercial", estilos["Subtitulo"]),
    ]

    titulo = [
        Paragraph("COMPROBANTE<br/>DE VENTA", estilos["TituloPDF"]),
        Spacer(1, 3 * mm),
        Paragraph(f"<b>N.º:</b> {escape(venta.numero)}", estilos["NormalPDF"]),
        Paragraph(
            f"<b>Fecha:</b> {timezone.localtime(venta.fecha).strftime('%d/%m/%Y %H:%M')}",
            estilos["NormalPDF"],
        ),
    ]

    encabezado = Table(
        [[empresa, titulo]],
        colWidths=[68 * mm, 60 * mm],
    )

    encabezado.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    elementos.append(encabezado)

    elementos.append(HRFlowable(
        width="100%",
        thickness=1.2,
        color=BORGOÑA,
        spaceAfter=5 * mm,
    ))

    # INFORMACIÓN DE LA VENTA

    informacion = [
        [
            Paragraph("<b>RESPONSABLE</b>", estilos["NormalPDF"]),
            Paragraph("<b>MÉTODO DE PAGO</b>", estilos["NormalPDF"]),
            Paragraph("<b>ESTADO</b>", estilos["NormalPDF"]),
        ],
        [
            Paragraph(escape(venta.usuario.username), estilos["NegritaPDF"]),
            Paragraph(escape(venta.get_metodo_pago_display()), estilos["NegritaPDF"]),
            Paragraph("<font color='#25804A'><b>CONFIRMADA</b></font>", estilos["NegritaPDF"]),
        ],
    ]

    tabla_info = Table(
        informacion,
        colWidths=[42 * mm, 43 * mm, 43 * mm],
    )

    tabla_info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIS_CLARO),
        ("BOX", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elementos.append(tabla_info)
    elementos.append(Spacer(1, 6 * mm))

    # PRODUCTOS

    elementos.append(Paragraph(
        "<b>DETALLE DE PRODUCTOS</b>",
        estilos["NegritaPDF"],
    ))

    elementos.append(Spacer(1, 3 * mm))

    datos = [[
        Paragraph("PRODUCTO", estilos["CabeceraTabla"]),
        Paragraph("CANT.", estilos["CabeceraTabla"]),
        Paragraph("PRECIO", estilos["CabeceraTabla"]),
        Paragraph("DESC.", estilos["CabeceraTabla"]),
        Paragraph("SUBTOTAL", estilos["CabeceraTabla"]),
    ]]

    for detalle in detalles:
        datos.append([
            Paragraph(escape(detalle.producto.nombre), estilos["TablaPDF"]),
            Paragraph(str(detalle.cantidad), estilos["TablaPDF"]),
            Paragraph(f"{detalle.precio_unitario:,.2f}", estilos["TablaPDF"]),
            Paragraph(f"{detalle.descuento:,.2f}", estilos["TablaPDF"]),
            Paragraph(f"{detalle.subtotal:,.2f}", estilos["NegritaPDF"]),
        ])

    tabla_productos = Table(
        datos,
        colWidths=[46 * mm, 13 * mm, 22 * mm, 19 * mm, 28 * mm],
        repeatRows=1,
    )

    tabla_productos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BORGOÑA),
        ("GRID", (0, 0), (-1, -1), 0.4, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elementos.append(tabla_productos)
    elementos.append(Spacer(1, 6 * mm))

    # RESUMEN

    resumen = [
        [
            Paragraph("Subtotal", estilos["NormalPDF"]),
            Paragraph(f"Bs {venta.subtotal:,.2f}", estilos["NormalPDF"]),
        ],
        [
            Paragraph("Descuento general", estilos["NormalPDF"]),
            Paragraph(f"Bs {venta.descuento:,.2f}", estilos["NormalPDF"]),
        ],
    ]

    tabla_resumen = Table(
        resumen,
        colWidths=[38 * mm, 30 * mm],
        hAlign="RIGHT",
    )

    tabla_resumen.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 2 * mm))

    total = Table(
        [[
            Paragraph("TOTAL PAGADO", estilos["NegritaPDF"]),
            Paragraph(f"Bs {venta.total:,.2f}", estilos["TotalPDF"]),
        ]],
        colWidths=[38 * mm, 30 * mm],
        hAlign="RIGHT",
    )

    total.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIS_CLARO),
        ("BOX", (0, 0), (-1, -1), 0.6, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elementos.append(total)

    # OBSERVACIONES

    if venta.observaciones:
        elementos.append(Spacer(1, 5 * mm))
        elementos.append(Paragraph("<b>OBSERVACIONES</b>", estilos["NegritaPDF"]))
        elementos.append(Spacer(1, 2 * mm))
        elementos.append(Paragraph(
            escape(venta.observaciones).replace("\n", "<br/>"),
            estilos["NormalPDF"],
        ))

    # PIE

    elementos.append(Spacer(1, 8 * mm))

    elementos.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=GRIS_LINEA,
        spaceAfter=3 * mm,
    ))

    elementos.append(Paragraph(
        "<b>¡Gracias por su compra!</b>",
        ParagraphStyle(
            "Gracias",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=BORGOÑA,
            alignment=TA_CENTER,
        ),
    ))

    elementos.append(Spacer(1, 2 * mm))

    elementos.append(Paragraph(
        "LICORERÍA HOMERO · Comprobante generado por el sistema.",
        ParagraphStyle(
            "Pie",
            fontSize=7,
            textColor=GRIS,
            alignment=TA_CENTER,
        ),
    ))

    documento.build(elementos)

    response.write(buffer.getvalue())
    buffer.close()

    return response
