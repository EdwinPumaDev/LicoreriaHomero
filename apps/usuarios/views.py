
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from apps.productos.models import Producto
from apps.ventas.models import Venta


@login_required
def dashboard(request):
    ventas_confirmadas = Venta.objects.filter(
        estado=Venta.Estado.CONFIRMADA
    )

    total_ventas = ventas_confirmadas.count()

    ingresos = ventas_confirmadas.aggregate(
        total=Sum("total")
    )["total"] or 0

    productos_activos = Producto.objects.filter(
        activo=True
    ).count()

    productos_bajo_stock = Producto.objects.filter(
        activo=True,
        stock__lte=models_stock_minimo(),
    ).count()

    ultimas_ventas = ventas_confirmadas.order_by(
        "-fecha"
    )[:5]

    contexto = {
        "total_ventas": total_ventas,
        "ingresos": ingresos,
        "productos_activos": productos_activos,
        "productos_bajo_stock": productos_bajo_stock,
        "ultimas_ventas": ultimas_ventas,
    }

    return render(request, "usuarios/dashboard.html", contexto)


def models_stock_minimo():
    from django.db.models import F
    return F("stock_minimo")
