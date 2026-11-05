from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.productos.models import Categoria, Marca, Producto
from apps.proveedores.models import Proveedor


class Command(BaseCommand):
    help = "Carga datos iniciales para la Licorería Homero (categorías, marcas, proveedores y productos base)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando carga de datos iniciales..."))

        # 1. Categorías
        categorias_data = [
            ("Singanis", "Singanis tradicionales y de altura de Bolivia"),
            ("Vinos", "Vinos tintos, blancos, rosados y oportos"),
            ("Cervezas", "Cervezas nacionales e importadas"),
            ("Whiskies", "Whiskies escoceses, bourbons y blended"),
            ("Fernet y Amargos", "Aperitivos, fernet y digestivos"),
            ("Vodkas y Rones", "Destilados blancos y oscuros"),
            ("Licores y Cremas", "Licores dulces, cremas y anís"),
            ("Gaseosas y Aguas", "Mezcladores, sodas, agua tónica y mineral"),
            ("Hielo y Complementos", "Bolsas de hielo, vasos, snacks y complementos"),
        ]

        categorias_map = {}
        for nombre, desc in categorias_data:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre, defaults={"descripcion": desc, "activo": True}
            )
            categorias_map[nombre] = cat

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(categorias_map)} categorias listas."))

        # 2. Marcas
        marcas_data = [
            ("Casa Real", "Singani de Tarija, Bolivia"),
            ("Los Parrales", "Singani de altura Tarija"),
            ("Campos de Solana", "Vinos tarijenos de altura"),
            ("Kohlberg", "Bodega y vinedos de Tarija"),
            ("Pacena", "Cerveceria Boliviana Nacional"),
            ("Huari", "Cerveza premium de origen boliviano"),
            ("Corona", "Cerveza mexicana extra"),
            ("Johnnie Walker", "Whisky escoces"),
            ("Branca", "Fernet Branca tradicional"),
            ("Flor de Cana", "Ron nicaraguense"),
            ("Absolut", "Vodka sueco"),
            ("Coca-Cola", "Bebidas carbonatadas"),
        ]

        marcas_map = {}
        for nombre, desc in marcas_data:
            m, _ = Marca.objects.get_or_create(
                nombre=nombre, defaults={"descripcion": desc, "activo": True}
            )
            marcas_map[nombre] = m

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(marcas_map)} marcas listas."))

        # 3. Proveedores de prueba
        proveedores_data = [
            {
                "nombre": "Distribuidora D&M Bolivia S.R.L.",
                "nit": "1023849021",
                "persona_contacto": "Carlos Mendoza",
                "telefono": "71234567",
                "correo": "ventas@dymbolivia.com",
                "direccion": "Av. Blanco Galindo Km 3",
            },
            {
                "nombre": "Cerveceria Boliviana Nacional S.A. (CBN)",
                "nit": "1015694028",
                "persona_contacto": "Marina Rocha",
                "telefono": "72983741",
                "correo": "pedidos@cbn.bo",
                "direccion": "Av. Montes N. 500",
            },
            {
                "nombre": "Sociedad Agroindustrial del Valle (Casa Real)",
                "nit": "1004829103",
                "persona_contacto": "Roberto Granier",
                "telefono": "70654321",
                "correo": "contacto@casareal.bo",
                "direccion": "Valle de Santa Ana, Tarija",
            },
        ]

        for prov_item in proveedores_data:
            Proveedor.objects.get_or_create(
                nit=prov_item["nit"],
                defaults=prov_item,
            )

        self.stdout.write(self.style.SUCCESS("[OK] Proveedores base listos."))

        # 4. Productos de muestra
        productos_data = [
            {
                "codigo": "SING-CR-ET-750",
                "codigo_barras": "7771001000101",
                "nombre": "Singani Casa Real Etiqueta Negra 750ml",
                "descripcion": "Singani de uva Moscatel de Alejandria, triple destilado",
                "categoria": categorias_map["Singanis"],
                "marca": marcas_map["Casa Real"],
                "unidad_medida": Producto.UnidadMedida.BOTELLA,
                "costo": Decimal("48.00"),
                "precio_venta": Decimal("65.00"),
                "stock": 24,
                "stock_minimo": 6,
            },
            {
                "codigo": "SING-CR-RO-750",
                "codigo_barras": "7771001000102",
                "nombre": "Singani Casa Real Etiqueta Roja 750ml",
                "descripcion": "Singani clasico para chuflay",
                "categoria": categorias_map["Singanis"],
                "marca": marcas_map["Casa Real"],
                "unidad_medida": Producto.UnidadMedida.BOTELLA,
                "costo": Decimal("38.00"),
                "precio_venta": Decimal("50.00"),
                "stock": 3,  # Stock bajo intencional para ver el KPI de alerta
                "stock_minimo": 6,
            },
            {
                "codigo": "FER-BR-750",
                "codigo_barras": "7790440200015",
                "nombre": "Fernet Branca 750ml",
                "descripcion": "Aperitivo amargo italiano a base de hierbas",
                "categoria": categorias_map["Fernet y Amargos"],
                "marca": marcas_map["Branca"],
                "unidad_medida": Producto.UnidadMedida.BOTELLA,
                "costo": Decimal("58.00"),
                "precio_venta": Decimal("75.00"),
                "stock": 18,
                "stock_minimo": 5,
            },
            {
                "codigo": "WHI-JW-RO-750",
                "codigo_barras": "5000267014203",
                "nombre": "Johnnie Walker Red Label 750ml",
                "descripcion": "Whisky escoces blended Red Label",
                "categoria": categorias_map["Whiskies"],
                "marca": marcas_map["Johnnie Walker"],
                "unidad_medida": Producto.UnidadMedida.BOTELLA,
                "costo": Decimal("78.00"),
                "precio_venta": Decimal("105.00"),
                "stock": 12,
                "stock_minimo": 4,
            },
            {
                "codigo": "CER-PAC-PIL-620",
                "codigo_barras": "7772002000019",
                "nombre": "Cerveza Pacena Pilsener 620ml",
                "descripcion": "Cerveza nacional en botella retornable",
                "categoria": categorias_map["Cervezas"],
                "marca": marcas_map["Pacena"],
                "unidad_medida": Producto.UnidadMedida.BOTELLA,
                "costo": Decimal("11.50"),
                "precio_venta": Decimal("15.00"),
                "stock": 48,
                "stock_minimo": 12,
            },
            {
                "codigo": "VIN-CS-TRI-750",
                "codigo_barras": "7773003000028",
                "nombre": "Vino Campos de Solana TRI Varietal Tinto 750ml",
                "descripcion": "Vino de corte Tannat, Malbec y Petit Verdot",
                "categoria": categorias_map["Vinos"],
                "marca": marcas_map["Campos de Solana"],
                "unidad_medida": Producto.UnidadMedida.BOTELLA,
                "costo": Decimal("62.00"),
                "precio_venta": Decimal("85.00"),
                "stock": 2,  # Stock bajo intencional
                "stock_minimo": 4,
            },
            {
                "codigo": "REF-CC-2L",
                "codigo_barras": "7774004000037",
                "nombre": "Coca-Cola Original 2 Litros Retornable",
                "descripcion": "Gaseosa mezcladora clasica",
                "categoria": categorias_map["Gaseosas y Aguas"],
                "marca": marcas_map["Coca-Cola"],
                "unidad_medida": Producto.UnidadMedida.BOTELLA,
                "costo": Decimal("8.50"),
                "precio_venta": Decimal("11.00"),
                "stock": 30,
                "stock_minimo": 10,
            },
        ]

        creados = 0
        for p_data in productos_data:
            prod, created = Producto.objects.get_or_create(
                codigo=p_data["codigo"],
                defaults=p_data,
            )
            if created:
                creados += 1

        self.stdout.write(
            self.style.SUCCESS(f"[OK] Catalogo base cargado: {creados} productos nuevos.")
        )
        self.stdout.write(self.style.SUCCESS("[OK] Base de datos lista para pruebas!"))

