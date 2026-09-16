import flet as ft

from ui.theme import BORDER, PRIMARY, SUCCESS, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


def _product_image(producto, compact):
    thumbnail = producto.get("thumbnail")
    if thumbnail:
        return ft.Image(
            src=thumbnail,
            height=100 if compact else 126,
            fit=ft.ImageFit.CONTAIN,
        )

    return ft.Container(
        height=100 if compact else 126,
        alignment=ft.alignment.center,
        content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, size=42, color=TEXT_SECONDARY),
    )


def build_product_card(producto, on_view=None, compact=False):
    def handle_view(_):
        if on_view:
            on_view(producto)

    return ft.Container(
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=16,
        padding=14,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color="#18000000",
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            controls=[
                ft.Container(
                    content=_product_image(producto, compact),
                    bgcolor="#0A1624",
                    border_radius=12,
                    alignment=ft.alignment.center,
                    padding=7,
                ),
                ft.Text(
                    producto["categoria"],
                    size=11,
                    color=PRIMARY,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    height=42,
                    content=ft.Text(
                        producto["nombre"],
                        size=15,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_600,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            f"Q{producto['precio']:.2f}",
                            size=17,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            f"{producto['existencia']} disponibles",
                            size=11,
                            color=SUCCESS if producto["existencia"] > 0 else TEXT_SECONDARY,
                        ),
                    ],
                ),
                ft.TextButton(
                    "Ver producto",
                    icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                    on_click=handle_view,
                    style=ft.ButtonStyle(color=PRIMARY),
                ),
            ],
            spacing=7,
        ),
    )
