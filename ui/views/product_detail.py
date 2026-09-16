import flet as ft

from ui.theme import (
    BORDER,
    PRIMARY,
    SECONDARY,
    SUCCESS,
    SURFACE,
    SURFACE_ELEVATED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    WARNING,
)


def normalize_quantity(quantity, stock):
    stock = max(0, int(stock))
    if stock == 0:
        return 1
    return min(max(1, int(quantity)), stock)


def build_product_detail_view(
    producto,
    quantity,
    on_quantity_change,
    on_buy,
    on_search_alternatives,
    on_back,
    layout_mode="wide",
):
    stock = max(0, int(producto["existencia"]))
    selected_quantity = normalize_quantity(quantity, stock)
    thumbnail = producto.get("thumbnail")

    visual = (
        ft.Image(src=thumbnail, fit=ft.ImageFit.CONTAIN)
        if thumbnail
        else ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, size=72, color=TEXT_SECONDARY)
    )

    quantity_text = ft.Text(
        str(selected_quantity),
        width=42,
        size=17,
        color=TEXT_PRIMARY,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )
    decrease_button = ft.IconButton(
        icon=ft.Icons.REMOVE_ROUNDED,
        icon_color=TEXT_PRIMARY,
        disabled=selected_quantity <= 1 or stock == 0,
        tooltip="Disminuir cantidad",
    )
    increase_button = ft.IconButton(
        icon=ft.Icons.ADD_ROUNDED,
        icon_color=PRIMARY,
        disabled=selected_quantity >= stock or stock == 0,
        tooltip="Aumentar cantidad",
    )

    def update_quantity(new_quantity):
        nonlocal selected_quantity
        selected_quantity = normalize_quantity(new_quantity, stock)
        quantity_text.value = str(selected_quantity)
        decrease_button.disabled = selected_quantity <= 1 or stock == 0
        increase_button.disabled = selected_quantity >= stock or stock == 0
        on_quantity_change(selected_quantity)
        quantity_text.update()
        decrease_button.update()
        increase_button.update()

    decrease_button.on_click = lambda _: update_quantity(selected_quantity - 1)
    increase_button.on_click = lambda _: update_quantity(selected_quantity + 1)

    stock_available = stock > 0
    stock_color = SUCCESS if stock_available else WARNING
    stock_label = f"{stock} unidades disponibles" if stock_available else "Sin existencias"

    purchase_button = ft.FilledButton(
        "Comprar ahora",
        icon=ft.Icons.SHOPPING_BAG_ROUNDED,
        width=float("inf"),
        disabled=not stock_available,
        on_click=lambda _: on_buy(selected_quantity),
        style=ft.ButtonStyle(
            bgcolor=PRIMARY,
            color="#031018",
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
        ),
    )
    alternative_button = ft.OutlinedButton(
        "Buscar alternativas",
        icon=ft.Icons.TRAVEL_EXPLORE_ROUNDED,
        width=float("inf"),
        visible=not stock_available,
        on_click=lambda _: on_search_alternatives(),
        style=ft.ButtonStyle(color=SECONDARY, side=ft.BorderSide(1, SECONDARY)),
    )

    details = ft.Column(
        controls=[
            ft.Text(
                producto["categoria"],
                size=11,
                color=SECONDARY,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                producto["nombre"],
                size=30 if layout_mode == "wide" else 26,
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
                    ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=stock_color, size=18),
                    ft.Text(stock_label, color=stock_color, size=13),
                ],
                spacing=8,
            ),
            ft.Divider(color=BORDER, height=22),
            ft.Text("Cantidad", size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_600),
            ft.Container(
                bgcolor=SURFACE,
                border=ft.border.all(1, BORDER),
                border_radius=14,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                content=ft.Row(
                    controls=[decrease_button, quantity_text, increase_button],
                    spacing=2,
                    tight=True,
                ),
            ),
            ft.Container(height=4),
            ft.Container(width=float("inf"), content=purchase_button),
            ft.Container(width=float("inf"), content=alternative_button, visible=not stock_available),
        ],
        spacing=12,
    )

    return ft.Column(
        controls=[
            ft.TextButton(
                "Volver a Productos",
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                on_click=lambda _: on_back(),
            ),
            ft.Container(
                bgcolor=SURFACE_ELEVATED,
                border=ft.border.all(1, BORDER),
                border_radius=22,
                padding=20 if layout_mode == "narrow" else 26,
                content=ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            col={"xs": 12, "md": 6},
                            height=280 if layout_mode == "narrow" else 360,
                            padding=20,
                            bgcolor="#0A1624",
                            border_radius=18,
                            alignment=ft.alignment.center,
                            content=visual,
                        ),
                        ft.Container(
                            col={"xs": 12, "md": 6},
                            padding=12 if layout_mode == "narrow" else 18,
                            content=details,
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
