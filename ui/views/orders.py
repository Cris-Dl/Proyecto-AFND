import flet as ft

from ui.theme import BORDER, PRIMARY, SUCCESS, SURFACE, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


def _order_card(order, on_track):
    in_transit = order.estado_afnd == "q5"
    delivered = order.estado_afnd == "q6"
    status_label = "En ruta" if in_transit else "Entregado" if delivered else "Procesando"
    status_color = PRIMARY if in_transit else SUCCESS if delivered else TEXT_SECONDARY

    return ft.Container(
        col={"xs": 12, "lg": 6},
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
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
                            content=ft.Icon(ft.Icons.LOCAL_SHIPPING_ROUNDED, color=status_color),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    f"Pedido #{order.id_pedido}",
                                    size=11,
                                    color=TEXT_SECONDARY,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(
                                    status_label,
                                    size=15,
                                    color=status_color,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_ROUNDED if delivered else ft.Icons.ROUTE_ROUNDED,
                            color=status_color,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Divider(color=BORDER, height=16),
                ft.Text(order.producto, size=17, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                ft.Row(
                    controls=[
                        ft.Text(f"Cantidad: {order.cantidad}", size=12, color=TEXT_SECONDARY),
                        ft.Container(expand=True),
                        ft.Text(f"Q{order.total:.2f}", size=18, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.FilledButton(
                    "Rastrear pedido",
                    icon=ft.Icons.MAP_ROUNDED,
                    visible=in_transit,
                    width=float("inf"),
                    on_click=lambda _: on_track(order.id_pedido),
                    style=ft.ButtonStyle(bgcolor=PRIMARY, color="#031018"),
                ),
            ],
            spacing=10,
        ),
    )


def build_orders_view(username, orders, on_login, on_track):
    if not username:
        return ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOCK_PERSON_ROUNDED, size=48, color=PRIMARY),
                    ft.Text("Inicia sesión para ver tus pedidos", size=22, color=TEXT_PRIMARY),
                    ft.Text(
                        "Tus compras y entregas aparecerán aquí.",
                        size=13,
                        color=TEXT_SECONDARY,
                    ),
                    ft.FilledButton(
                        "Iniciar sesión",
                        icon=ft.Icons.LOGIN_ROUNDED,
                        on_click=lambda _: on_login(),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                tight=True,
            ),
        )

    content = (
        ft.ResponsiveRow(
            controls=[_order_card(order, on_track) for order in orders],
            spacing=14,
            run_spacing=14,
        )
        if orders
        else ft.Container(
            bgcolor=SURFACE_ELEVATED,
            border=ft.border.all(1, BORDER),
            border_radius=18,
            padding=30,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=42, color=TEXT_SECONDARY),
                    ft.Text("Todavía no tienes pedidos", size=18, color=TEXT_PRIMARY),
                    ft.Text("Tu próxima compra aparecerá aquí.", size=12, color=TEXT_SECONDARY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                tight=True,
            ),
        )
    )

    return ft.Column(
        controls=[
            ft.Text("Pedidos", size=30, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text(f"Historial de {username}", size=12, color=TEXT_SECONDARY),
            content,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
