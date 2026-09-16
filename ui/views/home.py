import flet as ft

from ui.components.product_card import build_product_card
from ui.theme import BORDER, PRIMARY, SECONDARY, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY
from ui.views.common import build_status_panel


def _hero(on_explore):
    copy = ft.Container(
        col={"sm": 12, "md": 7},
        padding=ft.padding.symmetric(horizontal=10, vertical=16),
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
                    padding=ft.padding.symmetric(horizontal=13, vertical=7),
                ),
                ft.Text("GamerGear", size=42, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text("Juega sin límites", size=26, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                ft.Text(
                    "Descubre tecnología, accesorios y equipo seleccionado para llevar cada partida al siguiente nivel.",
                    size=14,
                    color=TEXT_SECONDARY,
                    max_lines=3,
                ),
                ft.FilledButton(
                    "Explorar productos",
                    icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                    on_click=lambda _: on_explore(),
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        color="#031018",
                        padding=ft.padding.symmetric(horizontal=22, vertical=16),
                    ),
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    visual = ft.Container(
        col={"sm": 12, "md": 5},
        height=250,
        alignment=ft.alignment.center,
        border_radius=22,
        bgcolor="#0A1726",
        border=ft.border.all(1, BORDER),
        content=ft.Stack(
            controls=[
                ft.Container(
                    width=184,
                    height=184,
                    border_radius=92,
                    bgcolor="#172E43",
                    alignment=ft.alignment.center,
                    content=ft.Icon(ft.Icons.SPORTS_ESPORTS_ROUNDED, size=96, color=PRIMARY),
                ),
                ft.Container(
                    right=22,
                    top=22,
                    content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=SECONDARY, size=26),
                ),
                ft.Container(
                    left=24,
                    bottom=20,
                    content=ft.Text("PERFORMANCE / PRECISIÓN", size=10, color=TEXT_SECONDARY),
                ),
            ],
        ),
    )

    return ft.Container(
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=24,
        padding=24,
        content=ft.ResponsiveRow(controls=[copy, visual], spacing=18, run_spacing=18),
    )


def _featured_content(productos, loading, error, on_retry, on_view):
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

    destacados = productos[:3]
    if not destacados:
        return build_status_panel(
            ft.Icons.INVENTORY_2_OUTLINED,
            "Catálogo sin productos",
            "No hay productos disponibles para mostrar en este momento.",
        )

    return ft.ResponsiveRow(
        controls=[
            ft.Container(
                col={"sm": 12, "md": 6, "lg": 4},
                content=build_product_card(producto, on_view=on_view, compact=True),
            )
            for producto in destacados
        ],
        spacing=18,
        run_spacing=18,
    )


def build_home_view(productos, loading, error, on_explore, on_retry, on_view):
    return ft.Column(
        controls=[
            _hero(on_explore),
            ft.Container(height=8),
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Productos destacados", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text("Una selección del catálogo GamerGear.", size=13, color=TEXT_SECONDARY),
                        ],
                        spacing=3,
                    ),
                    ft.Container(expand=True),
                    ft.TextButton("Ver catálogo", on_click=lambda _: on_explore()),
                ],
            ),
            _featured_content(productos, loading, error, on_retry, on_view),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
