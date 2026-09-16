import flet as ft

from ui.theme import BORDER, PRIMARY, SURFACE, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


NAV_ITEMS = (
    ("inicio", "Inicio", ft.Icons.HOME_ROUNDED),
    ("productos", "Productos", ft.Icons.STORE_ROUNDED),
    ("pedidos", "Pedidos", ft.Icons.RECEIPT_LONG_ROUNDED),
    ("perfil", "Perfil", ft.Icons.PERSON_ROUNDED),
)


def _nav_item(route, label, icon, selected, compact, on_navigate):
    is_selected = route == selected
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(
                    icon,
                    size=21,
                    color=PRIMARY if is_selected else TEXT_SECONDARY,
                ),
                ft.Text(
                    label,
                    size=14,
                    weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_400,
                    color=TEXT_PRIMARY if is_selected else TEXT_SECONDARY,
                    visible=not compact,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER if compact else ft.MainAxisAlignment.START,
            spacing=14,
        ),
        bgcolor=SURFACE_ELEVATED if is_selected else None,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=16, vertical=13),
        tooltip=label if compact else None,
        on_click=lambda _: on_navigate(route),
    )


def build_sidebar(selected, on_navigate, compact=False, secondary_items=None):
    secondary_items = secondary_items or []
    navigation = [
        _nav_item(route, label, icon, selected, compact, on_navigate)
        for route, label, icon in NAV_ITEMS
    ]

    secondary_controls = []
    if secondary_items:
        secondary_controls = [
            ft.Divider(color=BORDER, height=32),
            *[
                _nav_item(route, label, icon, selected, compact, on_navigate)
                for route, label, icon in secondary_items
            ],
        ]

    brand = ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.SPORTS_ESPORTS_ROUNDED, color=BACKGROUND, size=25),
                width=42,
                height=42,
                bgcolor=PRIMARY,
                border_radius=13,
                alignment=ft.alignment.center,
            ),
            ft.Text(
                "GamerGear",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=TEXT_PRIMARY,
                visible=not compact,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER if compact else ft.MainAxisAlignment.START,
        spacing=12,
    )

    return ft.Container(
        width=88 if compact else 244,
        bgcolor=SURFACE,
        border=ft.border.only(right=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=14, vertical=22),
        content=ft.Column(
            controls=[
                brand,
                ft.Container(height=28),
                *navigation,
                *secondary_controls,
                ft.Container(expand=True),
                ft.Text(
                    "Tu equipo. Tu juego.",
                    size=11,
                    color=TEXT_SECONDARY,
                    visible=not compact,
                ),
            ],
            spacing=7,
            expand=True,
        ),
    )
