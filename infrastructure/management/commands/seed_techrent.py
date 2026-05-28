from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from django.core.management.base import BaseCommand

from domain.enums import EquipoEstado, RolUsuario
from infrastructure.models import EquipoModel, UsuarioModel

# Catálogo base inicial
EQUIPOS_CATALOGO: list[dict] = [
    {"nombre": "MacBook Pro 16\"", "categoria": "Laptop", "precio_por_dia": Decimal("80.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Dell XPS 13", "categoria": "Laptop", "precio_por_dia": Decimal("60.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "iPad Pro 12.9\"", "categoria": "Tablet", "precio_por_dia": Decimal("40.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Canon EOS R5", "categoria": "Cámara", "precio_por_dia": Decimal("90.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Sony A7 IV", "categoria": "Cámara", "precio_por_dia": Decimal("85.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Laptop Gamer ASUS ROG", "categoria": "Laptop", "precio_por_dia": Decimal("95.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Lenovo ThinkPad X1 Carbon", "categoria": "Laptop", "precio_por_dia": Decimal("55.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "HP Spectre x360", "categoria": "Laptop", "precio_por_dia": Decimal("52.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Microsoft Surface Pro 9", "categoria": "Tablet", "precio_por_dia": Decimal("48.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Samsung Galaxy Tab S9", "categoria": "Tablet", "precio_por_dia": Decimal("35.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "iPhone 15 Pro Max", "categoria": "Smartphone", "precio_por_dia": Decimal("45.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Samsung Galaxy S24 Ultra", "categoria": "Smartphone", "precio_por_dia": Decimal("42.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Nikon Z8", "categoria": "Cámara", "precio_por_dia": Decimal("110.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "GoPro Hero 12", "categoria": "Cámara", "precio_por_dia": Decimal("25.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "DJI Mini 4 Pro", "categoria": "Drone", "precio_por_dia": Decimal("70.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "DJI Mavic 3 Pro", "categoria": "Drone", "precio_por_dia": Decimal("120.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Meta Quest 3", "categoria": "VR/AR", "precio_por_dia": Decimal("38.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Apple Vision Pro", "categoria": "VR/AR", "precio_por_dia": Decimal("150.00"), "estado": EquipoEstado.NO_DISPONIBLE},
    {"nombre": "PlayStation 5", "categoria": "Consola", "precio_por_dia": Decimal("30.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Xbox Series X", "categoria": "Consola", "precio_por_dia": Decimal("28.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Nintendo Switch OLED", "categoria": "Consola", "precio_por_dia": Decimal("22.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Proyector Epson 4K", "categoria": "Proyector", "precio_por_dia": Decimal("65.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "BenQ TK700 4K", "categoria": "Proyector", "precio_por_dia": Decimal("55.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Monitor LG UltraWide 38\"", "categoria": "Monitor", "precio_por_dia": Decimal("32.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Monitor Dell 4K 27\"", "categoria": "Monitor", "precio_por_dia": Decimal("28.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Teclado mecánico Keychron Q1", "categoria": "Periférico", "precio_por_dia": Decimal("8.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Micrófono Shure SM7B", "categoria": "Audio", "precio_por_dia": Decimal("18.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Stream Deck Elgato XL", "categoria": "Streaming", "precio_por_dia": Decimal("15.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Cámara web Logitech Brio 4K", "categoria": "Streaming", "precio_por_dia": Decimal("12.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Router WiFi 6E ASUS", "categoria": "Redes", "precio_por_dia": Decimal("10.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "NAS Synology DS923+", "categoria": "Almacenamiento", "precio_por_dia": Decimal("40.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "SSD Externo 4TB Samsung", "categoria": "Almacenamiento", "precio_por_dia": Decimal("6.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Impresora 3D Bambu Lab X1", "categoria": "Impresión", "precio_por_dia": Decimal("75.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Estación de soldadura Hakko", "categoria": "Electrónica", "precio_por_dia": Decimal("20.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Osciloscopio Rigol DS1054Z", "categoria": "Electrónica", "precio_por_dia": Decimal("35.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Tablet Wacom Cintiq 22", "categoria": "Diseño", "precio_por_dia": Decimal("50.00"), "estado": EquipoEstado.DISPONIBLE},
    {"nombre": "Mac Studio M2 Ultra", "categoria": "Desktop", "precio_por_dia": Decimal("130.00"), "estado": EquipoEstado.DISPONIBLE},
]

# 10 equipos adicionales por categoría (nombres únicos)
EQUIPOS_EXTRA_POR_CATEGORIA: dict[str, list[tuple[str, Decimal]]] = {
    "Laptop": [
        ("MSI Stealth 16 Studio", Decimal("92.00")),
        ("Acer Predator Helios 16", Decimal("78.00")),
        ("MacBook Air M3 15\"", Decimal("72.00")),
        ("Framework Laptop 16", Decimal("68.00")),
        ("Huawei MateBook X Pro", Decimal("58.00")),
        ("LG Gram 17 2024", Decimal("54.00")),
        ("Samsung Galaxy Book4 Ultra", Decimal("66.00")),
        ("Alienware m18 R2", Decimal("105.00")),
        ("Surface Laptop Studio 2", Decimal("74.00")),
        ("Lenovo Legion Pro 7i", Decimal("88.00")),
    ],
    "Tablet": [
        ("iPad Air M2 11\"", Decimal("32.00")),
        ("Lenovo Tab P12 Pro", Decimal("28.00")),
        ("Xiaomi Pad 6 Pro", Decimal("22.00")),
        ("OnePlus Pad 2", Decimal("24.00")),
        ("Amazon Fire Max 11", Decimal("12.00")),
        ("Huawei MatePad Pro 13.2", Decimal("30.00")),
        ("Galaxy Tab S9 FE+", Decimal("26.00")),
        ("Onyx Boox Tab Ultra C", Decimal("34.00")),
        ("reMarkable 2 Bundle", Decimal("20.00")),
        ("iPad mini 7", Decimal("25.00")),
    ],
    "Cámara": [
        ("Fujifilm X-T5 Kit", Decimal("78.00")),
        ("Panasonic Lumix S5 IIX", Decimal("82.00")),
        ("Canon EOS R6 Mark II", Decimal("95.00")),
        ("Sony FX3 Cinema", Decimal("125.00")),
        ("Blackmagic Pocket 6K G2", Decimal("115.00")),
        ("Insta360 X4", Decimal("38.00")),
        ("DJI Osmo Pocket 3", Decimal("42.00")),
        ("Leica Q3", Decimal("180.00")),
        ("Canon PowerShot V10", Decimal("28.00")),
        ("Sony ZV-E10 II", Decimal("48.00")),
    ],
    "Smartphone": [
        ("Google Pixel 9 Pro", Decimal("40.00")),
        ("iPhone 14 Pro", Decimal("38.00")),
        ("Xiaomi 14 Ultra", Decimal("36.00")),
        ("OnePlus 12", Decimal("32.00")),
        ("Nothing Phone 2a", Decimal("22.00")),
        ("Samsung Galaxy Z Fold 6", Decimal("65.00")),
        ("Motorola Edge 50 Pro", Decimal("28.00")),
        ("Huawei Pura 70 Pro", Decimal("42.00")),
        ("ASUS ROG Phone 8", Decimal("48.00")),
        ("Sony Xperia 1 VI", Decimal("44.00")),
    ],
    "Drone": [
        ("DJI Air 3 Fly More", Decimal("85.00")),
        ("Autel EVO Lite+", Decimal("72.00")),
        ("Parrot Anafi USA", Decimal("90.00")),
        ("DJI Avata 2", Decimal("68.00")),
        ("Skydio 2+ Kit", Decimal("95.00")),
        ("Holy Stone HS720E", Decimal("35.00")),
        ("DJI FPV Combo", Decimal("80.00")),
        ("PowerVision PowerEgg X", Decimal("55.00")),
        ("Hubsan Zino Mini Pro", Decimal("40.00")),
        ("DJI Phantom 4 Pro V2", Decimal("75.00")),
    ],
    "VR/AR": [
        ("PlayStation VR2", Decimal("35.00")),
        ("HTC Vive Pro 2", Decimal("55.00")),
        ("Pico 4 Enterprise", Decimal("42.00")),
        ("Valve Index Kit", Decimal("60.00")),
        ("Meta Quest 2 256GB", Decimal("28.00")),
        ("XREAL Air 2 Pro", Decimal("22.00")),
        ("Rokid Max AR", Decimal("25.00")),
        ("Lenovo ThinkReality VRX", Decimal("70.00")),
        ("Magic Leap 2", Decimal("95.00")),
        ("Snap Spectacles AR", Decimal("45.00")),
    ],
    "Consola": [
        ("Steam Deck OLED 1TB", Decimal("35.00")),
        ("ASUS ROG Ally X", Decimal("38.00")),
        ("PlayStation 5 Slim", Decimal("32.00")),
        ("Xbox Series S", Decimal("20.00")),
        ("Analogue Pocket", Decimal("18.00")),
        ("RetroN 5 Plus", Decimal("15.00")),
        ("Lenovo Legion Go", Decimal("36.00")),
        ("PlayStation Portal", Decimal("22.00")),
        ("Meta Quest 3S", Decimal("30.00")),
        ("Nintendo Switch Lite", Decimal("14.00")),
    ],
    "Proyector": [
        ("XGIMI Horizon Ultra", Decimal("58.00")),
        ("Optoma UHD55", Decimal("62.00")),
        ("Samsung The Freestyle 2", Decimal("38.00")),
        ("Anker Nebula Cosmos 4K", Decimal("52.00")),
        ("ViewSonic X1-4K", Decimal("48.00")),
        ("LG CineBeam HU710", Decimal("72.00")),
        ("BenQ GV30", Decimal("28.00")),
        ("Epson PowerLite 1795F", Decimal("45.00")),
        ("Nebula Capsule 3 Laser", Decimal("32.00")),
        ("JVC DLA-NZ7", Decimal("140.00")),
    ],
    "Monitor": [
        ("ASUS ProArt PA32UCX", Decimal("55.00")),
        ("Samsung Odyssey G9", Decimal("42.00")),
        ("Dell UltraSharp U3223QE", Decimal("38.00")),
        ("LG 27GP950-B", Decimal("30.00")),
        ("BenQ MOBIUZ EX3210U", Decimal("28.00")),
        ("Acer Predator X34", Decimal("34.00")),
        ("MSI MAG 321UPX", Decimal("36.00")),
        ("Apple Studio Display", Decimal("48.00")),
        ("Huawei MateView GT", Decimal("26.00")),
        ("ASUS ROG Swift PG27AQDM", Decimal("40.00")),
    ],
    "Periférico": [
        ("Logitech MX Master 3S", Decimal("6.00")),
        ("Razer DeathAdder V3 Pro", Decimal("5.00")),
        ("SteelSeries Apex Pro TKL", Decimal("9.00")),
        ("Logitech G Pro X Superlight", Decimal("5.00")),
        ("Wooting 60HE", Decimal("10.00")),
        ("Elgato Wave DX", Decimal("7.00")),
        ("Corsair K70 RGB Pro", Decimal("8.00")),
        ("Apple Magic Trackpad", Decimal("4.00")),
        ("Logitech Ergo K860", Decimal("6.00")),
        ("Razer Huntsman V3 Pro", Decimal("11.00")),
    ],
    "Audio": [
        ("Audio-Technica AT2020USB+", Decimal("12.00")),
        ("Rode NT-USB Mini", Decimal("14.00")),
        ("Beyerdynamic DT 900 Pro X", Decimal("16.00")),
        ("Sennheiser HD 660S2", Decimal("18.00")),
        ("Focusrite Scarlett 2i2 4th Gen", Decimal("15.00")),
        ("KRK Rokit 5 G4 Par", Decimal("22.00")),
        ("Zoom H6 Handy Recorder", Decimal("20.00")),
        ("Universal Audio Volt 276", Decimal("17.00")),
        ("JBL LSR305 MKII Par", Decimal("24.00")),
        ("Electro-Voice RE20", Decimal("19.00")),
    ],
    "Streaming": [
        ("Elgato Facecam Pro", Decimal("14.00")),
        ("Razer Kiyo Pro Ultra", Decimal("11.00")),
        ("ATEM Mini Pro ISO", Decimal("35.00")),
        ("Elgato Key Light Air", Decimal("10.00")),
        ("Tonor TC30 Boom Arm", Decimal("5.00")),
        ("Capture Card AVerMedia GC553G2", Decimal("16.00")),
        ("Rode Wireless GO II", Decimal("18.00")),
        ("Green Screen Elgato Collapsible", Decimal("8.00")),
        ("OBSBOT Tiny 4K", Decimal("20.00")),
        ("Loupedeck Live S", Decimal("25.00")),
    ],
    "Redes": [
        ("Ubiquiti UniFi Dream Machine", Decimal("18.00")),
        ("TP-Link Deco XE75 Mesh", Decimal("12.00")),
        ("Netgear Nighthawk AX12", Decimal("14.00")),
        ("Cisco Meraki MR46", Decimal("28.00")),
        ("MikroTik hAP ax3", Decimal("10.00")),
        ("Eero Pro 6E 3-pack", Decimal("15.00")),
        ("Starlink Gen 3 Kit", Decimal("45.00")),
        ("Peplink Balance 20X", Decimal("32.00")),
        ("Aruba Instant On AP22", Decimal("16.00")),
        ("GL.iNet Flint 2", Decimal("9.00")),
    ],
    "Almacenamiento": [
        ("WD Black SN850X 2TB", Decimal("8.00")),
        ("SanDisk Extreme PRO 2TB", Decimal("7.00")),
        ("LaCie Rugged 5TB", Decimal("12.00")),
        ("QNAP TS-464", Decimal("35.00")),
        ("Samsung T9 4TB", Decimal("9.00")),
        ("Crucial X10 Pro 2TB", Decimal("7.00")),
        ("OWC ThunderBay 8", Decimal("55.00")),
        ("Terramaster D5-300", Decimal("28.00")),
        ("Kingston DataTraveler Max 1TB", Decimal("5.00")),
        ("G-Technology ArmorATD 4TB", Decimal("11.00")),
    ],
    "Impresión": [
        ("Prusa MK4 Kit", Decimal("65.00")),
        ("Creality K1 Max", Decimal("55.00")),
        ("Formlabs Form 3+", Decimal("120.00")),
        ("Anycubic Photon M3 Max", Decimal("40.00")),
        ("Ultimaker S5", Decimal("95.00")),
        ("Elegoo Mars 4 Ultra", Decimal("32.00")),
        ("Raise3D Pro3 Plus", Decimal("110.00")),
        ("FlashForge Adventurer 5M", Decimal("38.00")),
        ("Markforged Onyx Pro", Decimal("130.00")),
        ("Snapmaker Artisan 3-in-1", Decimal("85.00")),
    ],
    "Electrónica": [
        ("Fluke 117 Multímetro", Decimal("15.00")),
        ("Uni-T UTG4082x Osciloscopio", Decimal("42.00")),
        ("Weller WE1010NA", Decimal("18.00")),
        ("ESP32 Dev Kit Bundle", Decimal("6.00")),
        ("Raspberry Pi 5 8GB Starter", Decimal("12.00")),
        ("Arduino Mega 2560 Kit", Decimal("8.00")),
        ("FNIRSI DSO152 Osciloscopio", Decimal("22.00")),
        ("Miniware TS101 Soldador", Decimal("14.00")),
        ("Siglent SDS1104X-E", Decimal("48.00")),
        ("Creality Ender S1 Pro", Decimal("35.00")),
    ],
    "Diseño": [
        ("XP-Pen Artist 24 Pro", Decimal("38.00")),
        ("Huion Kamvas Pro 24", Decimal("42.00")),
        ("iPad Pro M4 13\" + Pencil", Decimal("58.00")),
        ("CalDigit TS4 Thunderbolt", Decimal("20.00")),
        ("Xencelabs Pen Tablet Medium", Decimal("28.00")),
        ("Wacom Intuos Pro L", Decimal("22.00")),
        ("Loupedeck CT", Decimal("35.00")),
        ("BenQ PD3220U Designer", Decimal("40.00")),
        ("Mac mini M2 Pro", Decimal("45.00")),
        ("Contour Design RollerMouse", Decimal("8.00")),
    ],
    "Desktop": [
        ("Intel NUC 13 Extreme", Decimal("75.00")),
        ("HP Z2 Tower G9", Decimal("85.00")),
        ("Dell Precision 7865", Decimal("95.00")),
        ("Corsair One i500", Decimal("90.00")),
        ("Origin PC Neuron", Decimal("88.00")),
        ("Apple Mac Pro M2 Ultra", Decimal("200.00")),
        ("Lenovo ThinkStation P3", Decimal("70.00")),
        ("ASUS ProArt Station PD5", Decimal("78.00")),
        ("MSI Creator P100X", Decimal("82.00")),
        ("Falcon Northwest Tiki", Decimal("115.00")),
    ],
}


def _build_catalogo_completo() -> list[dict]:
    """Une catálogo base + 10 extras por categoría."""
    items = list(EQUIPOS_CATALOGO)
    for categoria, equipos in EQUIPOS_EXTRA_POR_CATEGORIA.items():
        for nombre, precio in equipos:
            estado = EquipoEstado.NO_DISPONIBLE if "Mac Pro" in nombre else EquipoEstado.DISPONIBLE
            items.append(
                {
                    "nombre": nombre,
                    "categoria": categoria,
                    "precio_por_dia": precio,
                    "estado": estado,
                }
            )
    return items


class Command(BaseCommand):
    help = "Crea o amplía el catálogo de equipos TechRent (use --append si ya hay datos)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--append",
            action="store_true",
            help="Agrega equipos nuevos sin borrar los existentes (por nombre único).",
        )

    def handle(self, *args, **options) -> None:
        append = options["append"]
        catalogo = _build_catalogo_completo()

        if EquipoModel.objects.exists() and not append:
            self.stdout.write(
                self.style.WARNING(
                    "Ya hay equipos en la BD. Ejecuta con --append para agregar el catálogo ampliado."
                )
            )
            return

        creados = 0
        omitidos = 0
        for item in catalogo:
            if EquipoModel.objects.filter(nombre=item["nombre"]).exists():
                omitidos += 1
                continue
            EquipoModel.objects.create(
                nombre=item["nombre"],
                categoria=item["categoria"],
                precio_por_dia=item["precio_por_dia"],
                estado=item["estado"].value,
            )
            creados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Equipos creados: {creados}. Omitidos (ya existían): {omitidos}. "
                f"Total en BD: {EquipoModel.objects.count()}."
            )
        )

        staff = [
            ("Vendedor TechRent", "vendor@techrent.com", RolUsuario.VENDOR),
            ("Admin TechRent", "admin@techrent.com", RolUsuario.ADMIN),
        ]
        for nombre, email, rol in staff:
            if not UsuarioModel.objects.filter(email=email).exists():
                UsuarioModel.objects.create(
                    nombre=nombre,
                    email=email,
                    fecha_registro=datetime.now(timezone.utc),
                    rol=rol.value,
                    activo=True,
                )
                self.stdout.write(self.style.SUCCESS(f"Usuario staff: {email} ({rol.value})"))
