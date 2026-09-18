import flet as ft

from ui.theme import BORDER, ERROR, PRIMARY, SUCCESS, SURFACE, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


OPTION_ICONS = {
    "S": ft.Icons.STORE_ROUNDED,
    "B": ft.Icons.WAREHOUSE_ROUNDED,
    "V": ft.Icons.LOCAL_SHIPPING_ROUNDED,
}


def _option_card(option, on_use):
    status_color = SUCCESS if option.available else ERROR
    status_label = "Disponible" if option.available else "No disponible"
    return ft.Container(
        col={"xs": 12, "md": 4},
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(2 if option.available else 1, status_color if option.available else BORDER),
        border_radius=18,
        padding=18,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=42,
                            height=42,
                            bgcolor=SURFACE,
                            border_radius=12,
                            alignment=ft.alignment.center,
                            content=ft.Icon(OPTION_ICONS[option.symbol], color=status_color),
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            bgcolor=SURFACE,
                            border=ft.border.all(1, BORDER),
                            border_radius=10,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            content=ft.Text(option.state, size=9, color=TEXT_SECONDARY),
                        ),
                    ]
                ),
                ft.Text(option.label, size=18, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Text("Evaluada", size=10, color=TEXT_SECONDARY),
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_ROUNDED
                            if option.available
                            else ft.Icons.CANCEL_OUTLINED,
                            size=17,
                            color=status_color,
                        ),
                        ft.Text(status_label, size=12, color=status_color, weight=ft.FontWeight.W_600),
                    ],
                    spacing=7,
                ),
                ft.FilledButton(
                    "Usar esta opción",
                    icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                    visible=option.available,
                    width=float("inf"),
                    on_click=lambda _, symbol=option.symbol: on_use(symbol),
                    style=ft.ButtonStyle(bgcolor=SUCCESS, color="#031018"),
                ),
            ],
            spacing=10,
        ),
    )


def build_alternatives_view(
    product,
    availability,
    cancelled,
    on_use,
    on_cancel_request,
    on_back,
):
    if cancelled:
        return ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Container(
                width=560,
                bgcolor=SURFACE_ELEVATED,
                border=ft.border.all(1, ERROR),
                border_radius=20,
                padding=30,
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CANCEL_ROUNDED, size=48, color=ERROR),
                        ft.Text("Pedido cancelado", size=26, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "No fue posible completar el pedido con las opciones simuladas.",
                            size=13,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text("Resultado AFND: RECHAZADA", size=11, color=ERROR, weight=ft.FontWeight.BOLD),
                        ft.OutlinedButton(
                            "Volver a Productos",
                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                            on_click=lambda _: on_back(),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=11,
                    tight=True,
                ),
            ),
        )

    no_solution = not availability.has_solution
    return ft.Column(
        controls=[
            ft.TextButton(
                "Volver al producto",
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                on_click=lambda _: on_back(),
            ),
            ft.Text("Buscar disponibilidad", size=30, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text("Simulación de disponibilidad alternativa", size=12, color=TEXT_SECONDARY),
            ft.Container(
                bgcolor=SURFACE,
                border=ft.border.all(1, BORDER),
                border_radius=14,
                padding=14,
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ALT_ROUTE_ROUNDED, color=PRIMARY),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "3 rutas posibles activas",
                                    size=14,
                                    color=PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"Evaluando alternativas para {product['nombre']}",
                                    size=11,
                                    color=TEXT_SECONDARY,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=11,
                ),
            ),
            ft.ResponsiveRow(
                controls=[_option_card(option, on_use) for option in availability.options],
                spacing=14,
                run_spacing=14,
            ),
            ft.Container(
                visible=no_solution,
                bgcolor="#301822",
                border=ft.border.all(1, ERROR),
                border_radius=14,
                padding=16,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "No se encontró disponibilidad en las opciones evaluadas.",
                            size=13,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.FilledButton(
                            "Cancelar solicitud",
                            icon=ft.Icons.CANCEL_ROUNDED,
                            on_click=lambda _: on_cancel_request(),
                            style=ft.ButtonStyle(bgcolor=ERROR, color="#16070B"),
                        ),
                    ],
                    spacing=10,
                ),
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
