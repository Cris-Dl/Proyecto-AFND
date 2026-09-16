import flet as ft

from ui.theme import BORDER, PRIMARY, SUCCESS, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


def build_product_detail_view(producto, on_back):
    thumbnail = producto.get("thumbnail")
    visual = (
        ft.Image(src=thumbnail, fit=ft.ImageFit.CONTAIN)
        if thumbnail
        else ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, size=72, color=TEXT_SECONDARY)
    )

    return ft.Column(
        controls=[
            ft.TextButton(
                "Volver a productos",
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                on_click=lambda _: on_back(),
            ),
            ft.Container(
                bgcolor=SURFACE_ELEVATED,
                border=ft.border.all(1, BORDER),
                border_radius=22,
                padding=26,
                content=ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            height=330,
                            padding=24,
                            bgcolor="#0A1624",
                            border_radius=18,
                            alignment=ft.alignment.center,
                            content=visual,
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            padding=18,
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        producto["categoria"],
                                        size=12,
                                        color=PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        producto["nombre"],
                                        size=30,
                                        color=TEXT_PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"Q{producto['precio']:.2f}",
                                        size=27,
                                        color=TEXT_PRIMARY,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=SUCCESS, size=18),
                                            ft.Text(
                                                f"{producto['existencia']} unidades disponibles",
                                                color=TEXT_SECONDARY,
                                            ),
                                        ]
                                    ),
                                    ft.Container(height=8),
                                    ft.Text(
                                        "La compra se habilitará en una fase posterior.",
                                        size=13,
                                        color=TEXT_SECONDARY,
                                    ),
                                ],
                                spacing=14,
                            ),
                        ),
                    ],
                    spacing=20,
                    run_spacing=20,
                ),
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
