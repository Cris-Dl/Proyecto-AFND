import flet as ft

from ui.theme import BORDER, PRIMARY, SECONDARY, SURFACE, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY
from ui.views.delivery_location import format_location


def build_order_review_view(
    usuario,
    producto,
    quantity,
    delivery_location,
    on_back,
    on_select_location,
    on_confirm,
    layout_mode="wide",
    supply_source=None,
):
    unit_price = producto["precio"]
    total = unit_price * quantity
    thumbnail = producto.get("thumbnail")
    visual = (
        ft.Image(src=thumbnail, fit=ft.ImageFit.CONTAIN)
        if thumbnail
        else ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, size=64, color=TEXT_SECONDARY)
    )

    def summary_line(label, value, emphasized=False):
        return ft.Row(
            controls=[
                ft.Text(label, size=13, color=TEXT_SECONDARY),
                ft.Container(expand=True),
                ft.Text(
                    value,
                    size=19 if emphasized else 14,
                    color=PRIMARY if emphasized else TEXT_PRIMARY,
                    weight=ft.FontWeight.BOLD if emphasized else ft.FontWeight.W_500,
                ),
            ],
            spacing=12,
        )

    actions = ft.ResponsiveRow(
        controls=[
            ft.Container(
                col={"xs": 12, "sm": 6},
                content=ft.OutlinedButton(
                    "Volver al producto",
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    width=float("inf"),
                    on_click=lambda _: on_back(),
                    style=ft.ButtonStyle(color=TEXT_SECONDARY, side=ft.BorderSide(1, BORDER)),
                ),
            ),
            ft.Container(
                col={"xs": 12, "sm": 6},
                content=ft.FilledButton(
                    "Confirmar pedido",
                    icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                    width=float("inf"),
                    disabled=delivery_location is None,
                    on_click=lambda _: on_confirm(),
                    style=ft.ButtonStyle(bgcolor=PRIMARY, color="#031018"),
                ),
            ),
        ],
        spacing=12,
        run_spacing=10,
    )

    return ft.Column(
        controls=[
            ft.Text("Revisar pedido", size=30, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Confirma los datos antes de continuar.",
                size=13,
                color=TEXT_SECONDARY,
            ),
            ft.Container(
                bgcolor=SURFACE_ELEVATED,
                border=ft.border.all(1, BORDER),
                border_radius=22,
                padding=20 if layout_mode == "narrow" else 26,
                content=ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            col={"xs": 12, "md": 5},
                            height=230 if layout_mode == "narrow" else 300,
                            padding=20,
                            bgcolor="#0A1624",
                            border_radius=18,
                            alignment=ft.alignment.center,
                            content=visual,
                        ),
                        ft.Container(
                            col={"xs": 12, "md": 7},
                            padding=12 if layout_mode == "narrow" else 18,
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        producto["categoria"],
                                        size=11,
                                        color=SECONDARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        producto["nombre"],
                                        size=23,
                                        color=TEXT_PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Container(
                                        bgcolor=SURFACE,
                                        border=ft.border.all(1, BORDER),
                                        border_radius=14,
                                        padding=16,
                                        content=ft.Column(
                                            controls=[
                                                summary_line("Usuario", usuario),
                                                summary_line("Cantidad", str(quantity)),
                                                summary_line("Precio unitario", f"Q{unit_price:.2f}"),
                                                ft.Divider(color=BORDER, height=18),
                                                summary_line("Total", f"Q{total:.2f}", emphasized=True),
                                            ],
                                            spacing=10,
                                        ),
                                    ),
                                    ft.Container(
                                        visible=bool(supply_source),
                                        bgcolor="#0D2B2A",
                                        border=ft.border.all(1, SECONDARY),
                                        border_radius=14,
                                        padding=14,
                                        content=ft.Column(
                                            controls=[
                                                ft.Text(
                                                    "Abastecimiento",
                                                    size=11,
                                                    color=TEXT_SECONDARY,
                                                ),
                                                ft.Text(
                                                    supply_source or "",
                                                    size=15,
                                                    color=TEXT_PRIMARY,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Text(
                                                    "Simulación de disponibilidad alternativa",
                                                    size=9,
                                                    color=SECONDARY,
                                                ),
                                            ],
                                            spacing=3,
                                        ),
                                    ),
                                    ft.Container(
                                        bgcolor=SURFACE,
                                        border=ft.border.all(1, PRIMARY if delivery_location else BORDER),
                                        border_radius=14,
                                        padding=16,
                                        content=ft.Column(
                                            controls=[
                                                ft.Text(
                                                    "Entrega",
                                                    size=14,
                                                    color=TEXT_PRIMARY,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(
                                                            ft.Icons.LOCATION_ON_ROUNDED,
                                                            color=PRIMARY if delivery_location else TEXT_SECONDARY,
                                                        ),
                                                        ft.Text(
                                                            format_location(delivery_location),
                                                            size=12,
                                                            color=(
                                                                TEXT_PRIMARY
                                                                if delivery_location
                                                                else TEXT_SECONDARY
                                                            ),
                                                        ),
                                                    ],
                                                    wrap=True,
                                                ),
                                                ft.OutlinedButton(
                                                    (
                                                        "Cambiar ubicación"
                                                        if delivery_location
                                                        else "Seleccionar ubicación de entrega"
                                                    ),
                                                    icon=ft.Icons.MAP_ROUNDED,
                                                    width=float("inf"),
                                                    on_click=lambda _: on_select_location(),
                                                    style=ft.ButtonStyle(
                                                        color=PRIMARY,
                                                        side=ft.BorderSide(1, PRIMARY),
                                                    ),
                                                ),
                                            ],
                                            spacing=10,
                                        ),
                                    ),
                                    ft.Container(height=2),
                                    actions,
                                ],
                                spacing=12,
                            ),
                        ),
                    ],
                    spacing=20,
                    run_spacing=20,
                ),
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
