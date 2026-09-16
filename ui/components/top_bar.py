import flet as ft

from ui.theme import BORDER, PRIMARY, SURFACE, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


def build_top_bar(usuario, on_account, on_search, compact=False):
    def submit_search(event):
        query = (event.control.value or "").strip()
        if query:
            on_search(query)

    account_text = usuario or "Iniciar sesión"
    account_icon = ft.Icons.ACCOUNT_CIRCLE_ROUNDED if usuario else ft.Icons.LOGIN_ROUNDED

    search = ft.TextField(
        hint_text="Buscar productos...",
        hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=13),
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        bgcolor=SURFACE_ELEVATED,
        border_radius=14,
        height=44,
        text_size=13,
        color=TEXT_PRIMARY,
        on_submit=submit_search,
    )

    account = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(account_icon, color=PRIMARY, size=21),
                ft.Text(
                    account_text,
                    color=TEXT_PRIMARY,
                    size=13,
                    weight=ft.FontWeight.W_500,
                    visible=not compact,
                ),
            ],
            spacing=9,
        ),
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=14,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        tooltip=account_text if compact else None,
        on_click=lambda _: on_account(),
    )

    return ft.Container(
        bgcolor=SURFACE,
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=14 if compact else 22, vertical=12),
        content=ft.Row(
            controls=[
                ft.Container(content=search, expand=True),
                account,
            ],
            spacing=16,
        ),
    )
