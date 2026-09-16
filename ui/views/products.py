import flet as ft

from ui.components.product_card import build_product_card
from ui.theme import BORDER, PRIMARY, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY
from ui.views.common import build_status_panel


def build_products_view(productos, loading, error, on_retry, on_view, initial_query="", columns=3):
    if loading:
        return build_status_panel(
            ft.Icons.DOWNLOADING_ROUNDED,
            "Cargando catálogo",
            "Consultando productos disponibles.",
        )

    if error:
        return build_status_panel(
            ft.Icons.CLOUD_OFF_ROUNDED,
            "No pudimos cargar el catálogo",
            error,
            action_label="Reintentar",
            on_action=on_retry,
        )

    results = ft.ResponsiveRow(spacing=18, run_spacing=18)
    count = ft.Text(size=12, color=TEXT_SECONDARY)

    def render_results(query, update=False):
        normalized = query.strip().casefold()
        filtered = [
            producto
            for producto in productos
            if normalized in producto["nombre"].casefold()
            or normalized in producto["categoria"].casefold()
        ]
        results.controls = [
            ft.Container(
                col=12 // columns,
                content=build_product_card(producto, on_view=on_view),
            )
            for producto in filtered
        ]
        count.value = f"{len(filtered)} productos"

        if not filtered:
            results.controls = [
                ft.Container(
                    col=12,
                    content=build_status_panel(
                        ft.Icons.SEARCH_OFF_ROUNDED,
                        "Sin coincidencias",
                        "Prueba con otro nombre o categoría.",
                    ),
                )
            ]

        if update:
            count.update()
            results.update()

    search = ft.TextField(
        value=initial_query,
        hint_text="Buscar por nombre o categoría",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        bgcolor=SURFACE_ELEVATED,
        border_radius=14,
        on_change=lambda event: render_results(event.control.value, update=True),
    )
    render_results(initial_query)

    return ft.Column(
        controls=[
            ft.Text("Productos", size=30, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text("Explora el catálogo disponible.", size=13, color=TEXT_SECONDARY),
            ft.Container(height=2),
            search,
            count,
            results,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
