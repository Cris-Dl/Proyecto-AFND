import flet as ft

from ui.components.product_card import build_product_card
from ui.theme import BORDER, PRIMARY, SECONDARY, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY
from ui.views.common import build_status_panel


TECH_CATEGORIES = (
    "Computadoras",
    "Teléfonos",
    "Tabletas",
    "Accesorios móviles",
)


def _technology_products(productos):
    return [
        producto
        for categoria in TECH_CATEGORIES
        for producto in productos
        if producto["categoria"] == categoria
    ]


def _featured_products(productos):
    technological = _technology_products(productos)
    technological_ids = {producto["id"] for producto in technological}
    fallback = [producto for producto in productos if producto["id"] not in technological_ids]
    return (technological + fallback)[:3]


def _hero_visual(productos):
    technological = _technology_products(productos)
    hero_product = technological[0] if technological else (productos[0] if productos else None)

    if hero_product and hero_product.get("thumbnail"):
        return ft.Stack(
            controls=[
                ft.Container(
                    left=12,
                    right=12,
                    top=8,
                    bottom=8,
                    alignment=ft.alignment.center,
                    content=ft.Image(
                        src=hero_product["thumbnail"],
                        fit=ft.ImageFit.CONTAIN,
                    ),
                ),
                ft.Container(
                    left=16,
                    bottom=12,
                    bgcolor="#D90A1726",
                    border_radius=14,
                    padding=ft.padding.symmetric(horizontal=11, vertical=6),
                    content=ft.Text(hero_product["categoria"], size=10, color=PRIMARY),
                ),
            ]
        )

    return ft.Stack(
        controls=[
            ft.Container(
                width=142,
                height=142,
                border_radius=71,
                bgcolor="#172E43",
                alignment=ft.alignment.center,
                content=ft.Icon(ft.Icons.SPORTS_ESPORTS_ROUNDED, size=72, color=PRIMARY),
            ),
            ft.Container(
                right=18,
                top=16,
                content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=SECONDARY, size=22),
            ),
        ],
    )


def _hero(productos, on_explore, wide_layout):
    copy = ft.Container(
        col=7 if wide_layout else 12,
        padding=ft.padding.symmetric(horizontal=8, vertical=8),
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "TECNOLOGÍA PARA JUGAR MEJOR",
                        size=11,
                        color=PRIMARY,
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor="#132D3B",
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=12, vertical=5),
                ),
                ft.Text("GamerGear", size=38, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text("Juega sin límites", size=23, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                ft.Text(
                    "Descubre tecnología, accesorios y equipo seleccionado para llevar cada partida al siguiente nivel.",
                    size=13,
                    color=TEXT_SECONDARY,
                    max_lines=2 if wide_layout else 3,
                ),
                ft.FilledButton(
                    "Explorar productos",
                    icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                    on_click=lambda _: on_explore(),
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        color="#031018",
                        padding=ft.padding.symmetric(horizontal=20, vertical=13),
                    ),
                ),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    visual = ft.Container(
        col=5 if wide_layout else 12,
        height=190 if wide_layout else 164,
        alignment=ft.alignment.center,
        border_radius=18,
        bgcolor="#0A1726",
        border=ft.border.all(1, BORDER),
        content=_hero_visual(productos),
    )

    return ft.Container(
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=22,
        padding=18,
        content=ft.ResponsiveRow(controls=[copy, visual], spacing=14, run_spacing=12),
    )


def _featured_content(productos, loading, error, on_retry, on_view, columns):
    if loading:
        return build_status_panel(
            ft.Icons.DOWNLOADING_ROUNDED,
            "Cargando selección",
            "Estamos preparando los productos destacados.",
        )

    if error:
        return build_status_panel(
            ft.Icons.CLOUD_OFF_ROUNDED,
            "No pudimos cargar el catálogo",
            error,
            action_label="Reintentar",
            on_action=on_retry,
        )

    destacados = _featured_products(productos)
    if not destacados:
        return build_status_panel(
            ft.Icons.INVENTORY_2_OUTLINED,
            "Catálogo sin productos",
            "No hay productos disponibles para mostrar en este momento.",
        )

    return ft.ResponsiveRow(
        controls=[
            ft.Container(
                col=12 // columns,
                content=build_product_card(producto, on_view=on_view, compact=True),
            )
            for producto in destacados
        ],
        spacing=18,
        run_spacing=18,
    )


def build_home_view(productos, loading, error, on_explore, on_retry, on_view, columns=3, wide_layout=True):
    return ft.Column(
        controls=[
            _hero(productos, on_explore, wide_layout),
            ft.Container(height=2),
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Productos destacados", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text("Una selección del catálogo GamerGear.", size=13, color=TEXT_SECONDARY),
                        ],
                        spacing=3,
                    ),
                    ft.Container(expand=True),
                    ft.TextButton("Ver catálogo", on_click=lambda _: on_explore()),
                ],
            ),
            _featured_content(productos, loading, error, on_retry, on_view, columns),
        ],
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
