import flet as ft

from ui.components.product_card import build_product_card
from ui.theme import BORDER, PRIMARY, SECONDARY, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY
from ui.views.common import build_status_panel


def build_products_view(
    productos,
    loading,
    error,
    on_retry,
    on_view,
    initial_query="",
    columns=3,
    demo_products=(),
):
    results = ft.ResponsiveRow(spacing=18, run_spacing=18)
    demo_results = ft.ResponsiveRow(spacing=18, run_spacing=18)
    count = ft.Text(size=12, color=TEXT_SECONDARY)

    demo_section = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Demo AFND", size=19, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        bgcolor="#241B46",
                        border=ft.border.all(1, SECONDARY),
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        content=ft.Text("SIMULACIÓN", size=9, color=SECONDARY, weight=ft.FontWeight.BOLD),
                    ),
                ],
                spacing=9,
                wrap=True,
            ),
            ft.Text(
                "Escenarios locales para demostrar disponibilidad alternativa; no representan inventario real.",
                size=11,
                color=TEXT_SECONDARY,
            ),
            demo_results,
        ],
        spacing=9,
    )

    if loading:
        catalog_content = build_status_panel(
            ft.Icons.DOWNLOADING_ROUNDED,
            "Cargando catálogo",
            "Consultando productos disponibles.",
        )
    elif error:
        catalog_content = build_status_panel(
            ft.Icons.CLOUD_OFF_ROUNDED,
            "No pudimos cargar el catálogo",
            error,
            action_label="Reintentar",
            on_action=on_retry,
        )
    else:
        catalog_content = results

    catalog_section = ft.Column(
        controls=[
            ft.Text("Catálogo", size=19, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text("Productos recibidos desde DummyJSON.", size=11, color=TEXT_SECONDARY),
            catalog_content,
        ],
        spacing=9,
    )

    def matches(product, normalized):
        return (
            normalized in product["nombre"].casefold()
            or normalized in product["categoria"].casefold()
        )

    def render_results(query, update=False):
        normalized = query.strip().casefold()
        filtered_demo = [product for product in demo_products if matches(product, normalized)]
        filtered_catalog = [product for product in productos if matches(product, normalized)]

        demo_results.controls = [
            ft.Container(
                col=12 // columns,
                content=build_product_card(product, on_view=on_view),
            )
            for product in filtered_demo
        ]
        demo_section.visible = bool(filtered_demo)

        if not loading and not error:
            results.controls = [
                ft.Container(
                    col=12 // columns,
                    content=build_product_card(product, on_view=on_view),
                )
                for product in filtered_catalog
            ]
            if not filtered_catalog:
                results.controls = [
                    ft.Container(
                        col=12,
                        content=build_status_panel(
                            ft.Icons.SEARCH_OFF_ROUNDED,
                            "Sin coincidencias en el catálogo",
                            "Prueba con otro nombre o categoría.",
                        ),
                    )
                ]

        count.value = f"{len(filtered_demo) + len(filtered_catalog)} resultados"
        if update:
            count.update()
            demo_section.update()
            if not loading and not error:
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
            demo_section,
            ft.Divider(color=BORDER, height=22),
            catalog_section,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
